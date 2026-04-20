import os
import re
import json
import requests
from urllib.parse import urlparse
from Tools.Ffuf import Ffuf
from Tools.XSStrike import XSStrike
from Tools.Sqlmap import Sqlmap
from Tools.RequestContext import RequestContext
from config import DEFAULT_URL, DEFAULT_THREADS, DEFAULT_RATE, DEFAULT_QUICK


def detect_extensions(base_url):
    try:
        resp = requests.get(base_url, timeout=5)
        server = resp.headers.get('Server', '').lower()
        powered_by = resp.headers.get('X-Powered-By', '').lower()
        if 'php' in powered_by:
            return '.php', 'PHP'
        if 'asp.net' in powered_by or 'microsoft-iis' in server:
            return '.aspx,.asmx', 'ASP.NET'
        if 'coyote' in server or 'tomcat' in server:
            return '.jsp,.do,.action', 'Java/Tomcat'
    except Exception:
        pass
    probe_map = [
        ('index.php', '.php', 'PHP'),
        ('index.jsp', '.jsp,.do,.action', 'Java/Tomcat'),
        ('index.aspx', '.aspx,.asmx', 'ASP.NET'),
    ]
    for filename, exts, label in probe_map:
        try:
            r = requests.get(base_url.rstrip('/') + '/' + filename, timeout=5)
            if r.status_code == 200:
                return exts, label
        except Exception:
            pass
    return None, None


def detect_language(base_url):
    try:
        resp = requests.get(base_url, timeout=5)
        lang = resp.headers.get('Content-Language', '').strip()
        if lang:
            return lang
        match = re.search(r'<html[^>]+lang=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None


def get_wordlist(scan_type, quick, lang_code):
    folder = 'quick' if quick else 'full'
    path = f'wordlists/{folder}/{lang_code}/{scan_type}.txt'
    if not os.path.exists(path):
        if lang_code != 'en':
            print(f"No {lang_code} wordlist for {scan_type} — falling back to English")
        path = f'wordlists/{folder}/en/{scan_type}.txt'
    return path


def run_scan(url=DEFAULT_URL, cookie=None, headers=None, quick=DEFAULT_QUICK, threads=DEFAULT_THREADS, rate=DEFAULT_RATE):
    url = re.sub(r'^https?://', '', url.strip())
    base_url = 'http://' + url

    result = {
        "target": base_url,
        "server_tech": None,
        "language": None,
        "queries_executed": [],
        "endpoints": {
            "directory": [],
            "file": [],
            "subdomain": []
        },
        "xss": {
            "confirmed": [],
            "potential": []
        },
        "sqli": {
            "confirmed": [],
            "potential": []
        }
    }

    ctx = RequestContext()
    if cookie:
        ctx.set_cookie(cookie)
    if headers:
        for h in headers:
            h = h.strip()
            if h:
                ctx.add_header(h)

    # Pre-phase: server tech + language detection
    extensions, tech_label = detect_extensions(base_url)
    result["server_tech"] = tech_label

    lang = detect_language(base_url)
    result["language"] = lang
    lang_code = lang.split('-')[0].lower() if lang else 'en'

    # Phase 1: endpoint discovery with ffuf (3 runs)
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
    result["queries_executed"].append(dir_command)
    print(f"Running: {dir_command}")
    os.system(dir_command)

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
    result["queries_executed"].append(file_command)
    print(f"Running: {file_command}")
    os.system(file_command)

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
    result["queries_executed"].append(sub_command)
    print(f"Running: {sub_command}")
    os.system(sub_command)

    # Phase 2: load results by category
    for fname, category in [
        ('results_directory.json', 'directory'),
        ('results_file.json', 'file'),
        ('results_subdomain.json', 'subdomain'),
    ]:
        if not os.path.exists(fname):
            print(f"{fname} not found — skipping")
            continue
        with open(fname) as f:
            data = json.load(f)
        result["endpoints"][category] = [r['url'] for r in data.get('results', []) if r['length'] > 0]

    all_endpoints = (
        result["endpoints"]["directory"] +
        result["endpoints"]["file"] +
        result["endpoints"]["subdomain"]
    )

    if not all_endpoints:
        print("No endpoints discovered.")
        return result

    # Phase 3: XSS with XSStrike
    with open('seeds.txt', 'w') as f:
        f.write('\n'.join(all_endpoints))

    xs = XSStrike()
    xs.addAttribute("url", base_url)
    xs.addAttribute("crawl")
    xs.addAttribute("level", 3)
    xs.addAttribute("seeds", "seeds.txt")
    xs.addAttribute("skip")
    ctx.apply_to_xsstrike(xs)
    xsstrike_command = xs.getCommandString()
    result["queries_executed"].append(xsstrike_command)
    print(f"\nRunning XSStrike: {xsstrike_command}")
    os.system(xsstrike_command + " > xss_output.txt")

    with open('xss_output.txt') as f:
        lines = f.readlines()
    result["xss"]["confirmed"] = [l.strip() for l in lines if '[++]' in l]
    result["xss"]["potential"] = [l.strip() for l in lines if 'potentially vulnerable' in l.lower()]

    # Phase 4: SQLi with sqlmap
    sqm = Sqlmap()
    sqm.addAttribute("urls_file", "seeds.txt")
    sqm.addAttribute("batch")
    sqm.addAttribute("forms")
    sqm.addAttribute("level", 1)
    sqm.addAttribute("risk", 1)
    ctx.apply_to_sqlmap(sqm)
    sqlmap_command = sqm.getCommandString()
    result["queries_executed"].append(sqlmap_command)
    print(f"\nRunning sqlmap: {sqlmap_command}")
    os.system(sqlmap_command + " > sqli_output.txt 2>&1")

    with open('sqli_output.txt', errors='ignore') as f:
        sqli_lines = f.readlines()
    result["sqli"]["confirmed"] = [l.strip() for l in sqli_lines if '[INFO]' in l and 'injectable' in l.lower()]
    result["sqli"]["potential"] = [l.strip() for l in sqli_lines if 'might be injectable' in l.lower()]

    return result


if __name__ == "__main__":
    url = input(f"Enter the base URL (http:// not needed) (press ENTER for default [{DEFAULT_URL}]): ").strip() or DEFAULT_URL

    cookie = input("Session cookie (ENTER to skip): ").strip() or None

    extra = input("Custom/auth headers, comma-separated (ENTER to skip)\n  e.g. Authorization: Bearer eyJ..., X-Api-Key: secret\n> ").strip()
    headers = [h.strip() for h in extra.split(",") if h.strip()] if extra else None

    quick = input("Quick scan? [y/N] (Default: No): ").strip().lower() == 'y'

    threads_input = input(f"Threads (press ENTER for default [{DEFAULT_THREADS}]): ").strip()
    threads = int(threads_input) if threads_input else DEFAULT_THREADS

    rate_input = input(f"Rate limit req/s (press ENTER for default [{DEFAULT_RATE}]): ").strip()
    rate = int(rate_input) if rate_input else DEFAULT_RATE

    result = run_scan(url, cookie=cookie, headers=headers, quick=quick, threads=threads, rate=rate)

    print(f"\nTarget: {result['target']}")
    print(f"Server tech: {result['server_tech'] or 'Unknown'}")
    print(f"Language: {result['language'] or 'Unknown'}")

    total = sum(len(v) for v in result['endpoints'].values())
    print(f"\nEndpoints found: {total}")
    for category, urls in result['endpoints'].items():
        if urls:
            print(f"  {category}: {len(urls)}")

    print("\n--- XSS Summary ---")
    if result['xss']['confirmed']:
        print(f"Confirmed: {len(result['xss']['confirmed'])}")
        for line in result['xss']['confirmed']:
            print(f"  {line}")
    elif result['xss']['potential']:
        print(f"Potentially vulnerable: {len(result['xss']['potential'])}")
        for line in result['xss']['potential']:
            print(f"  {line}")
    else:
        print("No XSS found.")

    print("\n--- SQLi Summary ---")
    if result['sqli']['confirmed']:
        print(f"Confirmed: {len(result['sqli']['confirmed'])}")
        for line in result['sqli']['confirmed']:
            print(f"  {line}")
    elif result['sqli']['potential']:
        print(f"Potentially vulnerable: {len(result['sqli']['potential'])}")
        for line in result['sqli']['potential']:
            print(f"  {line}")
    else:
        print("No SQLi found.")
