import os
import json
import requests
from Tools.Ffuf import Ffuf

default_url = 'testphp.vulnweb.com'
base_url = 'http://' + (input(f'Enter the base URL (https:// isn\'t need) (press ENTER for default [{default_url}]) : ') or default_url)
fuzz_url = base_url.rstrip('/') + '/FUZZ'

# Pre-phase: detect server tech to choose extensions automatically
def detect_extensions(base_url):
    try:
        resp = requests.get(base_url, timeout=5)
        server = resp.headers.get('Server', '').lower()
        powered_by = resp.headers.get('X-Powered-By', '').lower()
        if 'php' in powered_by:
            print("Detected: PHP  →  using .php")
            return '.php'
        if 'asp.net' in powered_by or 'microsoft-iis' in server:
            print("Detected: ASP.NET  →  using .aspx,.asmx")
            return '.aspx,.asmx'
        if 'coyote' in server or 'tomcat' in server:
            print("Detected: Java/Tomcat  →  using .jsp,.do,.action")
            return '.jsp,.do,.action'
    except Exception:
        pass
    print("No server tech detected  →  fuzzing bare paths only")
    return None

extensions = detect_extensions(base_url)

# Phase 1: discover endpoints with ffuf
ffuf_cmd = Ffuf()
ffuf_cmd.addAttribute("wordlist", "words.txt")
ffuf_cmd.addAttribute("target_url", fuzz_url)
ffuf_cmd.addAttribute("threads", 100)
ffuf_cmd.addAttribute("match_status", 200)
ffuf_cmd.addAttribute("follow_redirects")
ffuf_cmd.addAttribute("ignore_comments")
ffuf_cmd.addAttribute("non_interactive")
if extensions:
    ffuf_cmd.addAttribute("extensions", extensions)

command_string = ffuf_cmd.getCommandString() + " -o results.json -of json"
print(f'The command to execute is: {command_string}')
os.system(command_string)

# Phase 2: load discovered endpoints
if not os.path.exists('results.json'):
    print("results.json not found - ffuf likely failed. Check the command above.")
    exit()

with open('results.json') as f:
    data = json.load(f)

endpoints = [r['url'] for r in data.get('results', []) if r['length'] > 0]

if not endpoints:
    print("No endpoints discovered.")
    exit()

# Phase 3: detect method for each endpoint
def detect_method(url):
    # OPTIONS probe
    try:
        options_resp = requests.options(url, timeout=5)
        allow = options_resp.headers.get('Allow', '')
        if allow:
            found = []
            if 'GET' in allow:
                found.append('GET')
            if 'POST' in allow:
                found.append('POST')
            if found:
                return found
    except Exception:
        pass

    # GET probe - does a query param change the response?
    get_responsive = False
    try:
        baseline = requests.get(url, timeout=5)
        with_param = requests.get(url + '?test=1', timeout=5)
        get_responsive = (baseline.status_code != with_param.status_code or
                          len(baseline.text) != len(with_param.text))
    except Exception:
        pass

    # POST probe with body
    post_status = None
    try:
        post_resp = requests.post(url, data={'test': '1'}, timeout=5)
        post_status = post_resp.status_code
    except Exception:
        pass

    if post_status == 405:
        return ['GET']
    if post_status == 400:
        return ['POST']
    if post_status == 200 and get_responsive:
        return ['GET', 'POST']

    # 200 on POST just means the page rendered — not a POST signal
    return ['GET']

print("\n--- Method Detection ---")
results = []
for index, url in enumerate(endpoints):
    methods = detect_method(url)
    results.append((url, methods))
    print(f"{url}: accepts {', '.join(methods)}")
    print(f'progress: {index + 1}/ {len(endpoints)}')

# Summary
get_only  = [(url, m) for url, m in results if m == ['GET']]
post_only = [(url, m) for url, m in results if m == ['POST']]
both      = [(url, m) for url, m in results if 'GET' in m and 'POST' in m]

print("\n========== SUMMARY ==========")

print(f"\n[GET only] ({len(get_only)}) - potential reflected XSS / SQLi via query params")
for url, _ in get_only:
    print(f"  {url}")

print(f"\n[POST only] ({len(post_only)}) - form-based attacks")
for url, _ in post_only:
    print(f"  {url}")

print(f"\n[GET + POST] ({len(both)}) - both vectors possible")
for url, _ in both:
    print(f"  {url}")
