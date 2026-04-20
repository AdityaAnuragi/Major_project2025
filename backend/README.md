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

**Request body (JSON):**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | string | No | `demo.testfire.net` | Target domain (no `http://` needed) |
| `cookie` | string | No | — | Session cookie value, e.g. `JSESSIONID=abc123` |
| `headers` | string[] | No | — | Extra headers, e.g. `["Authorization: Bearer eyJ…"]` |
| `quick` | boolean | No | `false` | Use smaller wordlists for a faster scan |
| `threads` | number | No | `40` | ffuf thread count |
| `rate` | number | No | `100` | ffuf rate limit (req/s) |

**Example request:**
```json
{
  "url": "testphp.vulnweb.com",
  "quick": true
}
```

**Response:**
```json
{
  "target": "http://testphp.vulnweb.com",
  "server_tech": "PHP",
  "language": "en",
  "queries_executed": [
    "ffuf -w wordlists/full/en/directory.txt -u http://testphp.vulnweb.com/FUZZ ...",
    "ffuf -w wordlists/full/en/file.txt ...",
    "ffuf -w wordlists/full/en/subdomain.txt ...",
    "python vendor/XSStrike/xsstrike.py -u http://testphp.vulnweb.com --crawl ..."
  ],
  "endpoints": {
    "directory": ["http://testphp.vulnweb.com/admin/", "http://testphp.vulnweb.com/images/"],
    "file": ["http://testphp.vulnweb.com/search.php"],
    "subdomain": ["http://www.testphp.vulnweb.com/"]
  },
  "xss": {
    "confirmed": ["[++] XSS found at http://testphp.vulnweb.com/search.php?searchFor=…"],
    "potential": []
  },
  "sqli": {
    "confirmed": [],
    "potential": ["parameter 'id' might be injectable"]
  }
}
```
