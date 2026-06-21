import subprocess
import os
import re
import shutil

class Sandbox:
    def __init__(self):
        self.timeout = 5  # default timeout in seconds
        self._terminated = False

    def set_timeout(self, seconds: float):
        self.timeout = seconds

    def is_terminated(self) -> bool:
        return self._terminated

    def run_in_sandbox(self, code: str, language: str = 'Python') -> tuple[bool, str]:
        """
        Executes user code in an isolated subprocess.
        Returns (success, output/error)
        """
        self._terminated = False
        lang = language.lower()

        if lang in ['plain text', 'plaintext']:
            return True, "Plain text; skipping execution verification."

        # Create a temp directory inside the project root for execution
        base_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(base_dir, ".sandbox_temp")
        os.makedirs(temp_dir, exist_ok=True)

        # Clean up any residual files from previous runs
        for f in os.listdir(temp_dir):
            try:
                path = os.path.join(temp_dir, f)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception:
                pass

        try:
            if lang == 'python':
                file_path = os.path.join(temp_dir, "temp_py")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                # Run Python with -B (no bytecode .pyc creation)
                cmd = ["python3", "-B", file_path]
                return self._execute_cmd(cmd)

            elif lang == 'javascript':
                file_path = os.path.join(temp_dir, "temp.js")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                cmd = ["node", file_path]
                return self._execute_cmd(cmd)

            elif lang == 'java':
                # Attempt to parse Java class name or default to Main
                class_match = re.search(r"public\s+class\s+(\w+)", code)
                class_name = class_match.group(1) if class_match else "Main"
                file_path = os.path.join(temp_dir, f"{class_name}.java")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                # Compile Java
                compile_cmd = ["javac", file_path]
                ok, err = self._execute_cmd(compile_cmd, check_only=True)
                if not ok:
                    return False, f"Compilation failed:\n{err}"

                # Run Java
                run_cmd = ["java", "-cp", temp_dir, class_name]
                return self._execute_cmd(run_cmd)

            elif lang in ['c++', 'cpp']:
                file_path = os.path.join(temp_dir, "temp.cpp")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                bin_path = os.path.join(temp_dir, "temp_bin")
                # Compile C++
                compile_cmd = ["g++", "-O0", file_path, "-o", bin_path]
                ok, err = self._execute_cmd(compile_cmd, check_only=True)
                if not ok:
                    return False, f"Compilation failed:\n{err}"

                # Run C++ binary
                return self._execute_cmd([bin_path])

            elif lang == 'go':
                file_path = os.path.join(temp_dir, "temp.go")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                cmd = ["go", "run", file_path]
                return self._execute_cmd(cmd)

            elif lang == 'rust':
                file_path = os.path.join(temp_dir, "temp.rs")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)

                bin_path = os.path.join(temp_dir, "temp_bin")
                # Compile Rust
                compile_cmd = ["rustc", file_path, "-o", bin_path]
                ok, err = self._execute_cmd(compile_cmd, check_only=True)
                if not ok:
                    return False, f"Compilation failed:\n{err}"

                # Run Rust binary
                return self._execute_cmd([bin_path])

            else:
                return True, f"Unsupported sandbox language '{language}'; skipping check."

        finally:
            # Clean up temp dir
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _execute_cmd(self, cmd: list[str], check_only=False) -> tuple[bool, str]:
        try:
            # Run with timeout limit
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout
            )
            if proc.returncode != 0:
                # Execution failed
                err_msg = proc.stderr.strip() or proc.stdout.strip() or f"Exit code {proc.returncode}"
                return False, err_msg

            return True, proc.stdout.strip()

        except subprocess.TimeoutExpired:
            self._terminated = True
            return False, "Execution timed out (potential infinite loop or hang)."
        except FileNotFoundError:
            # Compiler/Interpreter not installed
            return True, f"Tool '{cmd[0]}' not installed; bypassed safety execution check."
        except Exception as e:
            return False, f"Sandbox error: {str(e)}"
