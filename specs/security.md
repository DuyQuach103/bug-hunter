# Security Architecture - Bug Hunter

This document details the multi-layered security pipelines implemented in Bug Hunter to prevent malicious code execution, handle runtime errors safely, and manage structured AI validations.

## The Security Pipeline

When code is submitted for analysis, it passes sequentially through the following gates before reaching the Gemini API:

```
[Code Submission]
       │
       ▼
┌──────────────┐
│Policy Server │ ──(Dangerous Code Match)──> [HTTP 400: Security Block]
└──────────────┘
       │
       ▼
┌──────────────┐
│Code Sanitizer│
└──────────────┘
       │
       ▼
┌──────────────┐
│Subprocess    │ ──(Crash / Infinite Loop)─> [HTTP 400: Sandbox Block]
│Sandbox       │
└──────────────┘
       │
       ▼
   [Passed] ────> [Gemini AI Analysis & Review]
```

---

## 1. Static Policy Check (`policy_server.py`)

The Policy Server acts as the first line of defense, checking for dangerous code patterns statically before any execution is attempted.

* **Pattern Rules**: Uses regular expressions to scan code for unsafe operations:
  * **Process Control**: Blocks `os.system`, `subprocess`, `shutil`, `pty`, `os.spawn`, etc.
  * **Dynamic Execution**: Blocks statements like `eval()`, `exec()`, `compile()`, and `__import__`.
  * **Networking**: Blocks raw socket creation (`socket.socket`, `socket.create_connection`) to prevent data exfiltration.
  * **Sensitive Files**: Blocks access to sensitive operating system configuration files (e.g. `/etc/passwd`).
* **Bypass Action**: If an unsafe match is detected, the pipeline halts immediately, returning an HTTP `400` status with a descriptive security block reason (e.g., `Dangerous operation detected: eval() function calls are blocked.`).

---

## 2. Sanitization

Before launching the script in the execution sandbox, the Policy Server sanitizes the code:
* Commenting out or neutralizing any recognized unsafe imports or statements.
* Ensuring that only safe structures are evaluated in the runtime phase.

---

## 3. Isolated Subprocess Sandbox (`sandbox.py`)

To catch execution-level crashes and resource exhaustion bugs (like infinite loops), the code is executed locally in a secure subprocess.

* **Runtime Verification**: The code is written to a temporary file and executed as a separate process (`python3 temp_file.py`).
* **Runtime Crash Interception**: If the code crashes (e.g. `ZeroDivisionError`, `IndexError`), the sandbox captures the stderr traceback and returns it to the client inside an HTTP `400` response.
* **Timeout Enforcement**: The process is capped at a strict execution timeout (default: `2.0 seconds`). If it exceeds this threshold, the subprocess is terminated, and a timeout error is returned. This prevents users from freezing the Flask server with infinite loops.

---

## 4. Smart Sandbox Bypass ("Ignore & Analyze Anyway")

While the sandbox is crucial for checking code functionality, some valid user code may fail verification (e.g. if it depends on missing external libraries, custom input files, or command-line parameters).

* **User Warning**: If validation fails due to a runtime crash or timeout, the frontend displays the error traceback in a banner.
* **Decoupled Bypass Option**: The banner includes a button labeled **"Ignore & Analyze Anyway"**.
* **Action**: Clicking this option makes a second API request to `/debug` with the parameter `skip_sandbox: true`. The backend bypasses the `Sandbox.run_in_sandbox()` check and directly queries Gemini, allowing the user to get an analysis despite the local execution failure.
