from flask import Flask, request
from flask_cors import CORS
from config import DEFAULT_URL, DEFAULT_THREADS, DEFAULT_RATE, DEFAULT_QUICK, RUN_DIR_FUZZ, RUN_FILE_FUZZ, RUN_SUBDOMAIN_FUZZ, RUN_XSS, RUN_SQLI
from script import run_scan

app = Flask(__name__)
CORS(app)


@app.get("/")
def health() -> tuple[dict, int]:
    print('inside health endpoint')
    return {"status": "ok"}, 200


@app.post("/scan")
def create_scan() -> tuple[dict, int]:
    data = request.get_json(silent=True) or {}
    print("Received:", data)

    url = data.get("url") or DEFAULT_URL
    cookie = data.get("cookie") or None
    headers = data.get("headers") or None
    quick = bool(data.get("quick", DEFAULT_QUICK))
    threads = int(data.get("threads", DEFAULT_THREADS))
    rate = int(data.get("rate", DEFAULT_RATE))
    run_dir_fuzz = bool(data.get("run_dir_fuzz", RUN_DIR_FUZZ))
    run_file_fuzz = bool(data.get("run_file_fuzz", RUN_FILE_FUZZ))
    run_subdomain_fuzz = bool(data.get("run_subdomain_fuzz", RUN_SUBDOMAIN_FUZZ))
    run_xss = bool(data.get("run_xss", RUN_XSS))
    run_sqli = bool(data.get("run_sqli", RUN_SQLI))

    print(f"Running scan -> url={url}, quick={quick}, threads={threads}, rate={rate}, cookie={cookie}, headers={headers}")
    print(f"  phases -> dir_fuzz={run_dir_fuzz}, file_fuzz={run_file_fuzz}, subdomain_fuzz={run_subdomain_fuzz}, xss={run_xss}, sqli={run_sqli}")
    result = run_scan(url, cookie=cookie, headers=headers, quick=quick, threads=threads, rate=rate,
                      run_dir_fuzz=run_dir_fuzz, run_file_fuzz=run_file_fuzz, run_subdomain_fuzz=run_subdomain_fuzz,
                      run_xss=run_xss, run_sqli=run_sqli)

    print('============ALL COMMANDS EXECUTED AND SENT TO CLIENT SUCCESSFULLY============')

    return result, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
