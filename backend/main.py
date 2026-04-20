from flask import Flask, request
from config import DEFAULT_URL

app = Flask(__name__)


@app.get("/")
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@app.post("/scan")
def create_scan() -> tuple[dict, int]:
    data = request.get_json(silent=True) or {}

    url = data.get("url") or DEFAULT_URL
    base_url = "http://" + url.lstrip("http://").lstrip("https://")

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

    return result, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)