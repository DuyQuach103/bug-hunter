from mcp.server.fastmcp import FastMCP
import urllib.request
import urllib.error
import json
import os

# Initialize the FastMCP server
mcp = FastMCP("BugHunter")

# Server endpoint URL config
SERVER_URL = os.environ.get("BUG_HUNTER_URL", "http://127.0.0.1:5001/debug")

@mcp.tool()
def debug_code(code: str, lang: str = "python") -> str:
    """
    Debugs code for errors, warnings, strengths, recommendations, and complexity.
    It executes validation and sandboxing checks before returning the analysis.
    
    Args:
        code: The source code snippet to analyze.
        lang: The programming language of the code (e.g. python, javascript, java, cpp, go, rust). Default is python.
    """
    payload = {
        "code": code,
        "lang": lang
    }
    
    req = urllib.request.Request(
        SERVER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read().decode("utf-8")
            data = json.loads(body)
            # Format output nicely for the user/model
            if "result" in data:
                return json.dumps(data["result"], indent=2)
            return json.dumps(data, indent=2)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err_data = json.loads(body)
            return f"Error ({e.code}): {json.dumps(err_data, indent=2)}"
        except json.JSONDecodeError:
            return f"HTTP Error {e.code}: {body}"
    except Exception as e:
        return (
            f"Connection Error: Could not connect to Bug Hunter server at {SERVER_URL}.\n"
            f"Please ensure the local Flask server is running (e.g. python server.py).\n"
            f"Details: {str(e)}"
        )

@mcp.tool()
def detect_language(code: str) -> str:
    """
    Auto-detects the programming language of a code snippet (Python, Java, JavaScript, C++, Go, or Rust).
    
    Args:
        code: The source code snippet to analyze.
    """
    scores = {
        "Python": 0,
        "Java": 0,
        "JavaScript": 0,
        "C++": 0,
        "Go": 0,
        "Rust": 0
    }
    evidence = {k: [] for k in scores.keys()}
    
    # Python
    if "def " in code:
        scores["Python"] += 3
        evidence["Python"].append("def keyword")
    if "print(" in code and "System.out" not in code and "fmt." not in code:
        scores["Python"] += 2
        evidence["Python"].append("print() function")
    if ":" in code and ("if " in code or "for " in code or "def " in code):
        scores["Python"] += 2
        evidence["Python"].append("block colon structure")
        
    # Java
    if "public class " in code:
        scores["Java"] += 5
        evidence["Java"].append("public class declaration")
    if "System.out.print" in code:
        scores["Java"] += 5
        evidence["Java"].append("System.out.println statement")
    if "String[] args" in code:
        scores["Java"] += 4
        evidence["Java"].append("main method arguments String[] args")
        
    # JavaScript
    if "console.log" in code:
        scores["JavaScript"] += 4
        evidence["JavaScript"].append("console.log() function")
    if "const " in code or "let " in code:
        scores["JavaScript"] += 3
        evidence["JavaScript"].append("let/const declaration")
    if "=>" in code:
        scores["JavaScript"] += 2
        evidence["JavaScript"].append("arrow function =>")
        
    # C++
    if "#include" in code:
        scores["C++"] += 4
        evidence["C++"].append("#include directive")
    if "std::" in code or "cout <<" in code:
        scores["C++"] += 4
        evidence["C++"].append("std::cout or namespace operators")
    if "using namespace" in code:
        scores["C++"] += 3
        evidence["C++"].append("using namespace directive")
        
    # Go
    if "package " in code:
        scores["Go"] += 4
        evidence["Go"].append("package declaration")
    if "func " in code and "fn " not in code:
        scores["Go"] += 3
        evidence["Go"].append("func keyword")
    if ":=" in code:
        scores["Go"] += 4
        evidence["Go"].append("short variable declaration :=")
    if "err != nil" in code:
        scores["Go"] += 5
        evidence["Go"].append("error check err != nil")
        
    # Rust
    if "fn " in code and "func " not in code:
        scores["Rust"] += 4
        evidence["Rust"].append("fn function declaration")
    if "let mut " in code:
        scores["Rust"] += 5
        evidence["Rust"].append("mutable variable definition let mut")
    if "println!" in code:
        scores["Rust"] += 5
        evidence["Rust"].append("println! macro")
        
    detected_lang = "Unknown"
    max_score = 0
    for lang, score in scores.items():
        if score > max_score:
            max_score = score
            detected_lang = lang
            
    if max_score == 0:
        return "Detected: Unknown\nConfidence: 0%\nEvidence: No clear language signature identified."
        
    confidence = min(max_score * 20, 99)
    evidence_str = ", ".join(evidence[detected_lang])
    return f"Detected: {detected_lang}\nConfidence: {confidence}%\nEvidence: {evidence_str}"

if __name__ == "__main__":
    mcp.run()
