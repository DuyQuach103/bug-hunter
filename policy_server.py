import re
import json
import datetime

class PolicyServer:
    @staticmethod
    def is_safe(code: str) -> tuple[bool, str]:
        """
        Scans code for dangerous operations.
        Returns (is_safe, error_reason)
        """
        if not code:
            return True, ""

        blocked_patterns = [
            ("eval(", "eval() function calls"),
            ("exec(", "exec() function calls"),
            ("compile(", "compile() function calls"),
            ("__import__", "direct __import__ calls"),
            ("os.system", "os.system calls"),
            ("subprocess", "subprocess module usage"),
            ("import socket", "socket network module imports"),
            ("from socket", "socket network module imports"),
            ("import requests", "requests HTTP library imports"),
            ("from requests", "requests HTTP library imports"),
            ("import urllib", "urllib network module imports"),
            ("from urllib", "from urllib network imports"),
            ("import http", "http client network module imports"),
            ("from http", "from http client network imports"),
            ("import subprocess", "subprocess module imports"),
            ("from subprocess", "from subprocess module imports"),
        ]

        # Scan for direct patterns
        for pattern, reason in blocked_patterns:
            if pattern in code:
                return False, f"Dangerous operation detected: {reason} are blocked."

        # Scan for file write operations: open(...) with write/append/exclusive/updating modes ('w', 'a', 'x', '+')
        write_mode_pattern = r"open\s*\([^)]*['\"]\s*[^'\"]*[wax+][^'\"]*['\"]"
        if re.search(write_mode_pattern, code):
            return False, "Dangerous operation detected: File write/append/exclusive operations are blocked."

        return True, ""

    @staticmethod
    def sanitize_code(code: str) -> str:
        """
        Dulls and disarms dangerous operations in user code.
        """
        if not code:
            return code

        replacements = {
            "eval(": "/* blocked */ eval_disabled(",
            "exec(": "/* blocked */ exec_disabled(",
            "compile(": "/* blocked */ compile_disabled(",
            "__import__": "/* blocked */ __import_disabled__",
            "os.system": "/* blocked */ os_system_disabled",
            "import socket": "# import socket (blocked)",
            "from socket": "# from socket (blocked)",
            "import requests": "# import requests (blocked)",
            "from requests": "# from requests (blocked)",
            "import urllib": "# import urllib (blocked)",
            "from urllib": "# from urllib (blocked)",
            "import http": "# import http (blocked)",
            "from http": "# from http (blocked)",
            "import subprocess": "# import subprocess (blocked)",
            "from subprocess": "# from subprocess (blocked)"
        }

        sanitized = code
        for pattern, replacement in replacements.items():
            sanitized = sanitized.replace(pattern, replacement)

        # Disarm file write operations by converting write/append/exclusive modes to read-only 'r'
        sanitized = re.sub(
            r"(open\s*\([^)]*['\"])\s*[^'\"]*[wax+][^'\"]*(['\"])",
            r"\1r\2",
            sanitized
        )

        return sanitized

    @staticmethod
    def log_request(user_id: str, code: str, result: str) -> None:
        """
        Logs request information into audit.log file for security audits.
        """
        import os
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_id": user_id or "anonymous",
            "code": code,
            "result_status": result
        }

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            audit_file = os.path.join(base_dir, "audit.log")
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Failed to write request to audit log: {e}")
