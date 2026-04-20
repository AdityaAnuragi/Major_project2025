import os
import re
import json
import requests  # used for server tech detection (pre-phase)
from urllib.parse import urlparse
from Tools.Ffuf import Ffuf
from Tools.XSStrike import XSStrike
from Tools.Sqlmap import Sqlmap
from Tools.RequestContext import RequestContext
from config import DEFAULT_URL, DEFAULT_THREADS, DEFAULT_RATE, DEFAULT_QUICK

base_url = 'http://' + (input(f'Enter the base URL (http:// isn\'t need) (press ENTER for default [{DEFAULT_URL}]) : ') or DEFAULT_URL)

ctx = RequestContext()

cookie = input("Session cookie (ENTER to skip): ").strip()
if cookie:
    ctx.set_cookie(cookie)

extra = input("Custom/auth headers, comma-separated (ENTER to skip)\n  e.g. Authorization: Bearer eyJ..., X-Api-Key: secret\n> ").strip()
if extra:
    for h in extra.split(","):
        h = h.strip()
        if h:
            ctx.add_header(h)

quick = input("Quick scan? [y/N] (Default: No): ").strip().lower() == 'y' or DEFAULT_QUICK

threads_input = input(f"Threads (press ENTER for default [{DEFAULT_THREADS}]): ").strip()
threads = int(threads_input) if threads_input else DEFAULT_THREADS

rate_input = input(f"Rate limit req/s (press ENTER for default [{DEFAULT_RATE}]): ").strip()
rate = int(rate_input) if rate_input else DEFAULT_RATE

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
    probe_map = [
        ('index.php', '.php', 'PHP (probed)'),
        ('index.jsp', '.jsp,.do,.action', 'Java/Tomcat (probed)'),
        ('index.aspx', '.aspx,.asmx', 'ASP.NET (probed)'),
    ]
    for filename, exts, label in probe_map:
        try:
            r = requests.get(base_url.rstrip('/') + '/' + filename, timeout=5)
            if r.status_code == 200:
                print(f"Detected: {label}  →  using {exts}")
                return exts
        except Exception:
            pass
    print("No server tech detected  →  fuzzing bare paths only")
    return None

extensions = detect_extensions(base_url)

def detect_language(base_url):
    try:
        resp = requests.get(base_url, timeout=5)
        lang = resp.headers.get('Content-Language', '').strip()
        if lang:
            print(f"Detected language: {lang}")
            return lang
        match = re.search(r'<html[^>]+lang=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
        if match:
            lang = match.group(1).strip()
            print(f"Detected language: {lang}")
            return lang
    except Exception:
        pass
    print("Language: not detected")
    return None

lang = detect_language(base_url)
lang_code = lang.split('-')[0].lower() if lang else 'en'

def get_wordlist(scan_type, quick, lang_code):
    folder = 'quick' if quick else 'full'
    path = f'wordlists/{folder}/{lang_code}/{scan_type}.txt'
    if not os.path.exists(path):
        if lang_code != 'en':
            print(f"No {lang_code} wordlist for {scan_type} — falling back to English")
        path = f'wordlists/{folder}/en/{scan_type}.txt'
    return path

# Phase 1: discover endpoints with ffuf (3 passes)

# Run 1: Directory fuzzing (extension fuzzing aswell)
print("\n--- Directory fuzzing ---")
dir_cmd = Ffuf()
dir_cmd.addAttribute("wordlist", get_wordlist('directory', quick, lang_code))
dir_cmd.addAttribute("target_url", base_url.rstrip('/') + '/FUZZ')
dir_cmd.addAttribute("threads", threads)
dir_cmd.addAttribute("rate", rate)
dir_cmd.addAttribute("match_status", 200)
dir_cmd.addAttribute("ignore_comments")
dir_cmd.addAttribute("non_interactive")
dir_cmd.addAttribute("auto_calibrate")
if extensions:
    dir_cmd.addAttribute("extensions", extensions)
ctx.apply_to_ffuf(dir_cmd)
dir_command = dir_cmd.getCommandString() + " -o results_directory.json -of json"
print(f'The command to execute is: {dir_command}')
os.system(dir_command)

# Run 2: File fuzzing
print("\n--- File fuzzing ---")
file_cmd = Ffuf()
file_cmd.addAttribute("wordlist", get_wordlist('file', quick, lang_code))
file_cmd.addAttribute("target_url", base_url.rstrip('/') + '/FUZZ')
file_cmd.addAttribute("threads", threads)
file_cmd.addAttribute("rate", rate)
file_cmd.addAttribute("match_status", 200)
file_cmd.addAttribute("ignore_comments")
file_cmd.addAttribute("non_interactive")
file_cmd.addAttribute("auto_calibrate")
ctx.apply_to_ffuf(file_cmd)
file_command = file_cmd.getCommandString() + " -o results_file.json -of json"
print(f'The command to execute is: {file_command}')
os.system(file_command)

# Run 3: Subdomain fuzzing
print("\n--- Subdomain fuzzing ---")
hostname = urlparse(base_url).hostname
subdomain_url = f"http://FUZZ.{hostname}/"
sub_cmd = Ffuf()
sub_cmd.addAttribute("wordlist", get_wordlist('subdomain', quick, lang_code))
sub_cmd.addAttribute("target_url", subdomain_url)
sub_cmd.addAttribute("threads", threads)
sub_cmd.addAttribute("rate", rate)
sub_cmd.addAttribute("match_status", 200)
sub_cmd.addAttribute("ignore_comments")
sub_cmd.addAttribute("non_interactive")
sub_cmd.addAttribute("auto_calibrate")
ctx.apply_to_ffuf(sub_cmd)
sub_command = sub_cmd.getCommandString() + " -o results_subdomain.json -of json"
print(f'The command to execute is: {sub_command}')
os.system(sub_command)

# Phase 2: merge all discovered endpoints
endpoints = []
for fname in ['results_directory.json', 'results_file.json', 'results_subdomain.json']:
    if not os.path.exists(fname):
        print(f"{fname} not found - skipping")
        continue
    with open(fname) as f:
        data = json.load(f)
    endpoints += [r['url'] for r in data.get('results', []) if r['length'] > 0]

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
os.system(xsstrike_command + " > xss_output.txt")

with open('xss_output.txt') as f:
    lines = f.readlines()

confirmed = [l.strip() for l in lines if '[++]' in l]
potential = [l.strip() for l in lines if 'potentially vulnerable' in l.lower()]

print("\n--- XSS Scan Summary ---")
if confirmed:
    print(f"Confirmed XSS: {len(confirmed)}")
    for line in confirmed:
        print(f"  {line}")
elif potential:
    print(f"Potentially vulnerable: {len(potential)}")
    for line in potential:
        print(f"  {line}")
else:
    print("No XSS vulnerabilities found.")

# Phase 4: SQL injection detection with sqlmap
print("\n--- SQL Injection Detection ---")
sqm = Sqlmap()
sqm.addAttribute("urls_file", "seeds.txt")
sqm.addAttribute("batch")
sqm.addAttribute("forms")
sqm.addAttribute("level", 1)
sqm.addAttribute("risk", 1)
ctx.apply_to_sqlmap(sqm)

sqlmap_command = sqm.getCommandString()
print(f'Running sqlmap: {sqlmap_command}')
os.system(sqlmap_command + " > sqli_output.txt 2>&1")

with open('sqli_output.txt', errors='ignore') as f:
    sqli_lines = f.readlines()

sqli_confirmed = [l.strip() for l in sqli_lines if '[INFO]' in l and 'injectable' in l.lower()]
sqli_potential = [l.strip() for l in sqli_lines if 'might be injectable' in l.lower()]

print("\n--- SQLi Scan Summary ---")
if sqli_confirmed:
    print(f"Confirmed SQLi: {len(sqli_confirmed)} parameter(s) found vulnerable")
    for line in sqli_confirmed:
        print(f"  {line}")
elif sqli_potential:
    print(f"Potentially vulnerable: {len(sqli_potential)} parameter(s) flagged")
    for line in sqli_potential:
        print(f"  {line}")
else:
    print("No SQL injection vulnerabilities found.")
