# Setup

After cloning the project, run the following commands once to get everything ready.

---

## 1. Install project dependencies

**Windows & Mac:**
```bash
pip install -r requirements.txt
```

---

## 2. Set up XSStrike

**Windows & Mac:**
```bash
git clone https://github.com/s0md3v/XSStrike.git vendor/XSStrike
pip install -r vendor/XSStrike/requirements.txt
```

---

## 3. Set up sqlmap

**Windows & Mac:**
```bash
git clone https://github.com/sqlmapproject/sqlmap.git vendor/sqlmap
```

---

That's it. You're good to go.

---

## 4. Run the server

```bash
python main.py
```

Server starts on `http://localhost:5000`.

---

# API

## `GET /`

Health check.

**Response:**
```json
{ "status": "ok" }
```

---

## `POST /scan`

Run a full reconnaissance scan against a target.

**Request body (JSON) — all fields optional:**

| Field | Type | Default | Description |
|---|---|---|---|
| `url` | string | `demo.testfire.net` | Target domain (`http://` not needed) |
| `cookie` | string | — | Session cookie, e.g. `JSESSIONID=abc123` |
| `headers` | string[] | — | Extra headers, e.g. `["Authorization: Bearer eyJ…"]` |
| `quick` | boolean | `true` | Use smaller wordlists for faster scan |
| `threads` | number | `100` | ffuf thread count |
| `rate` | number | `100` | ffuf rate limit (req/s) |
| `run_dir_fuzz` | boolean | `true` | Run directory fuzzing (ffuf) |
| `run_file_fuzz` | boolean | `false` | Run file fuzzing (ffuf) |
| `run_subdomain_fuzz` | boolean | `false` | Run subdomain fuzzing (ffuf) |
| `run_xss` | boolean | `true` | Run XSS scan (XSStrike) |
| `run_sqli` | boolean | `false` | Run SQLi scan (sqlmap) |

**Recommended request — send empty body, defaults are already tuned for demo:**
```json
{}
```

Defaults applied when fields are omitted:
- `url` → `demo.testfire.net`
- `quick` → `true`
- `threads` → `100`
- `rate` → `100`
- `run_dir_fuzz` → `true`
- `run_file_fuzz` → `false`
- `run_subdomain_fuzz` → `false`
- `run_xss` → `true`
- `run_sqli` → `false`

**Response shape:**
```json
{
  "target": "http://demo.testfire.net",
  "server_tech": "Java/Tomcat",
  "language": "en",
  "queries_executed": [
    "ffuf -w wordlists/quick/en/directory.txt:FUZZ -u http://demo.testfire.net/FUZZ ...",
    "python vendor/XSStrike/xsstrike.py -u http://demo.testfire.net --crawl -l 3 --seeds seeds.txt --skip",
    "python vendor/sqlmap/sqlmap.py -u http://demo.testfire.net -m seeds.txt --batch --forms --crawl=2 ..."
  ],
  "endpoints": {
    "directory": ["http://demo.testfire.net/bank/"],
    "file": ["http://demo.testfire.net/style.css"],
    "subdomain": []
  },
  "xss": {
    "confirmed": [
      "[++] Vulnerable webpage: http://demo.testfire.net/search.jsp",
      "[++] Vector for query: <hTMl/+/onMOUsEoVER%09=%09confirm()//"
    ],
    "potential": [
      "Potentially vulnerable objects found at http://demo.testfire.net/swagger/index.html"
    ]
  },
  "sqli": {
    "confirmed": [],
    "potential": []
  }
}
```
