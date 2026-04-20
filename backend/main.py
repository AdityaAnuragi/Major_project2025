from flask import Flask, request
from flask_cors import CORS
from config import DEFAULT_URL, DEFAULT_THREADS, DEFAULT_RATE, DEFAULT_QUICK
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

    url = data.get("url") or DEFAULT_URL
    cookie = data.get("cookie") or None
    headers = data.get("headers") or None
    quick = bool(data.get("quick", DEFAULT_QUICK))
    threads = int(data.get("threads", DEFAULT_THREADS))
    rate = int(data.get("rate", DEFAULT_RATE))

    result = run_scan(url, cookie=cookie, headers=headers, quick=quick, threads=threads, rate=rate)

    return result, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)