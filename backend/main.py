from flask import Flask, request

import subprocess
import os

app = Flask(__name__)


@app.get("/")
def health() -> tuple[dict, int]:
    print("Inside the health check GET endpoint")
    
    result = subprocess.run(
        ["ffuf", "-V"],
        capture_output=True,
        text=True,
        check=True
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    return {"status": "ok"}, 200


@app.post("/jobs")
def create_job() -> tuple[dict, int]:
    """Accept job options and respond with the parsed timeout."""
    data = request.get_json(silent=True) or {}
    timeout = data.get("timeout") or 10

    print(data, timeout)

    # Basic validation: ensure timeout is a positive number.
    # try:
    #     timeout_val = float(timeout)
    # except (TypeError, ValueError):
    #     return {"error": "timeout must be a number"}, 400
    
    command = ["ffuf", "-u", "https://example.com/FUZZ", "-w", "words.txt", "-timeout", str(timeout)]
    commandAsAString = " ".join(command)
    print(commandAsAString)
    
    # Option 1: Capture all output (buffered, waits for completion)
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    
    # ffuf sends progress and status to stderr, not stdout
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    # Option 2: For real-time streaming output (uncomment if you want to see progress as it happens):
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
    #                           text=True, bufsize=1, universal_newlines=True)
    # output_lines = []
    # for line in process.stdout:
    #     print(line, end='')  # Print in real-time
    #     output_lines.append(line)
    # process.wait()
    # full_output = ''.join(output_lines)

    # os.system('fuff -h')

    return {"received_timeout": timeout, "commandPreview": commandAsAString}, 200

    # return {"status": "ok"}, 200

if __name__ == "__main__":
    # Bind to all interfaces for container/VM use; adjust as needed.
    app.run(host="0.0.0.0", port=5000, debug=True)