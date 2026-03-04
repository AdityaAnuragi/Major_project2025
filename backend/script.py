import os
import json
import requests  # used for server tech detection (pre-phase)
from Tools.Ffuf import Ffuf
from Tools.XSStrike import XSStrike
from Tools.RequestContext import RequestContext

default_url = 'testphp.vulnweb.com'
base_url = 'http://' + (input(f'Enter the base URL (http:// isn\'t need) (press ENTER for default [{default_url}]) : ') or default_url)
fuzz_url = base_url.rstrip('/') + '/FUZZ'

ctx = RequestContext()

cookie = input("Session cookie (ENTER to skip): ").strip()
if cookie:
    ctx.set_cookie(cookie)

bearer = input("Bearer token (ENTER to skip): ").strip()
if bearer:
    ctx.set_bearer(bearer)

extra = input("Custom headers as 'Key: Value', comma-separated (ENTER to skip): ").strip()
if extra:
    for h in extra.split(","):
        h = h.strip()
        if h:
            ctx.add_header(h)

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
ctx.apply_to_ffuf(ffuf_cmd)

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

# Phase 3: crawl with XSStrike using ffuf-discovered endpoints as seeds
with open('seeds.txt', 'w') as f:
    f.write('\n'.join(endpoints))

xs = XSStrike()
xs.addAttribute("url", base_url)
xs.addAttribute("crawl")
xs.addAttribute("level", 3)
xs.addAttribute("seeds", "seeds.txt")
xs.addAttribute("skip")
ctx.apply_to_xsstrike(xs)

xsstrike_command = xs.getCommandString()
print(f'\nRunning XSStrike: {xsstrike_command}')
os.system(xsstrike_command)
