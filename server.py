import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from policy_server import PolicyServer
from sandbox import Sandbox

# Load environment variables from .env file if present
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Attempt to configure the Gemini client
# We support google-genai (new SDK) as primary, and google-generativeai (legacy SDK) as fallback
GEMINI_CLIENT = None
LEGACY_GENAI = False

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

try:
    from google import genai
    from google.genai import types
    if api_key:
        GEMINI_CLIENT = genai.Client(api_key=api_key)
except (ImportError, ValueError):
    pass

# Setup legacy fallback if client is not configured
try:
    if not GEMINI_CLIENT:
        import google.generativeai as legacy_genai
        if api_key:
            legacy_genai.configure(api_key=api_key)
        LEGACY_GENAI = True
except ImportError:
    pass

# Define Pydantic models for structured output
class BugIssue(BaseModel):
    description: str = Field(description="Description of the issue found")
    line: Optional[int] = Field(description="Line number where the issue occurs (1-indexed), or null if not applicable")
    fix: str = Field(description="Suggested code change or correction to fix this specific issue")

class AnalysisResult(BaseModel):
    syntax_errors: List[BugIssue] = Field(description="Syntax errors that make the code invalid or crash on execution")
    logic_errors: List[BugIssue] = Field(description="Logical flaws, incorrect assumptions, or incorrect math/conditional operations")
    performance_issues: List[BugIssue] = Field(description="Inefficient practices, unnecessary loops, or performance bottlenecks")
    security_issues: List[BugIssue] = Field(description="Vulnerabilities, dangerous functions, or unsafe imports/usage")
    strengths: List[str] = Field(description="Positive qualities of the code, clean design, or correct logical parts")
    recommendations: List[str] = Field(description="General improvements, style formatting recommendations, or refactoring tips")
    time_complexity: str = Field(description="Estimated Time Complexity in Big O notation (e.g., O(n), O(1))")
    space_complexity: str = Field(description="Estimated Space Complexity in Big O notation (e.g., O(n), O(1))")
    quality_score: int = Field(description="Code quality score from 1 (poor, full of bugs) to 10 (excellent, production-ready)")
    fixed_code: str = Field(description="The complete, fully corrected source code in the target language. Keep inline comments extremely brief and only on complex lines. Place any detailed explanations at the end under a block comment header: EXPLANATION (YOU CAN REMOVE). Raw code, no markdown blocks.")

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/debug', methods=['GET', 'POST'])
def serve_debug():
    if request.method == 'POST':
        return analyze_code()
    return send_from_directory(app.static_folder, 'debug.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_route():
    return analyze_code()

@app.route('/eval', methods=['POST'])
def run_evaluation():
    """Run all tests and return results."""
    from eval.run_tests import run_all_tests
    results = run_all_tests()
    return jsonify(results)

def analyze_code():
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({
            "error": "Security: Invalid request",
            "details": "No code provided"
        }), 400

    code = data['code']
    if not code.strip():
        return jsonify({
            "error": "Security: Invalid request",
            "details": "Provided code is empty"
        }), 400

    # Retrieve language parameter ('lang' or 'language')
    language = data.get('language') or data.get('lang') or 'Python'

    # Policy Server safety check
    is_safe, reason = PolicyServer.is_safe(code)
    if not is_safe:
        PolicyServer.log_request("anonymous", code, f"BLOCKED: {reason}")
        return jsonify({
            "error": "Security: Dangerous operation detected",
            "details": reason
        }), 400

    # Sanitize the code
    sanitized_code = PolicyServer.sanitize_code(code)

    # Run code in isolated Sandbox environment
    skip_sandbox = data.get('skip_sandbox', False)
    if not skip_sandbox:
        sandbox = Sandbox()
        sandbox.set_timeout(5.0)  # 5 seconds execution limit
        success, output = sandbox.run_in_sandbox(sanitized_code, language)
        if not success:
            PolicyServer.log_request("anonymous", code, f"SANDBOX_FAILED: {output}")
            return jsonify({
                "error": "Execution Error / Infinite Loop detected",
                "details": output
            }), 400

    # Ensure API key exists
    current_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not current_key and not GEMINI_CLIENT:
        return jsonify({
            "error": "Configuration Error",
            "details": "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable on the server."
        }), 500

    # Determine commenting rules for the target language in fixed_code
    comment_char = '//'
    block_start = '/*'
    block_end = '*/'
    if language.lower() == 'python':
        comment_char = '#'
        block_start = '"""'
        block_end = '"""'
    elif language.lower() in ['plain text', 'plaintext']:
        comment_char = ''
        block_start = '-----'
        block_end = '-----'

    prompt = f"""
    You are an expert {language} code analyzer. Analyze the following {language} code for syntax errors, logic errors, performance bottlenecks, security vulnerabilities, strengths, and general improvement recommendations.
    
    Additionally, estimate the overall Time Complexity (in Big O notation), Space Complexity (in Big O notation), rate the overall code quality from 1 to 10, and provide the complete fully corrected version of the code in the 'fixed_code' field.
    
    Formatting rules for the 'fixed_code' field:
    1. Do NOT put long docstrings or inline explanations inside the code itself, as it makes the code look messy.
    2. If there are complex or tricky lines of code, write a very short inline comment (using '{comment_char}') right above or next to that specific line.
    3. Place any detailed explanation or walkthrough of the changes at the very end of the code, separated by a header block:
       {block_start} EXPLANATION (YOU CAN REMOVE) {block_end}
       All explanation lines under this header block MUST be commented out using '{comment_char}' (or within a block comment structure) so the code remains runnable when copied.
    
    {language} Code to analyze:
    ```{language.lower()}
    {sanitized_code}
    ```
    
    Provide your analysis conforming strictly to the requested JSON structure. Be specific with line numbers and provide exact fixes.
    """

    try:
        models_to_try = ['gemini-2.5-flash']
        
        if not LEGACY_GENAI:
            # Using the new google-genai SDK
            client = GEMINI_CLIENT or genai.Client(api_key=current_key)
            last_error = None
            for model_name in models_to_try:
                try:
                    print(f"Attempting analysis with model: {model_name}...")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=AnalysisResult,
                            temperature=0.1,
                        ),
                    )
                    result_data = json.loads(response.text)
                    PolicyServer.log_request("anonymous", code, "SUCCESS")
                    return jsonify({"result": result_data})
                except Exception as model_error:
                    print(f"Model {model_name} failed: {model_error}")
                    # Prioritize rate-limit errors for reporting
                    if last_error is None or "429" in str(model_error) or "RESOURCE_EXHAUSTED" in str(model_error):
                        last_error = model_error
            # If all models failed, raise the last encountered error
            raise last_error
        else:
            # Fallback to the legacy google-generativeai SDK
            last_error = None
            for model_name in models_to_try:
                try:
                    print(f"Attempting legacy analysis with model: {model_name}...")
                    model = legacy_genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            "response_mime_type": "application/json",
                            "response_schema": AnalysisResult if hasattr(legacy_genai, 'protos') else None
                        }
                    )
                    result_data = json.loads(response.text)
                    PolicyServer.log_request("anonymous", code, "SUCCESS")
                    return jsonify({"result": result_data})
                except Exception as model_error:
                    print(f"Legacy model {model_name} failed: {model_error}")
                    # Prioritize rate-limit errors for reporting
                    if last_error is None or "429" in str(model_error) or "RESOURCE_EXHAUSTED" in str(model_error):
                        last_error = model_error
            # If all models failed, raise the last encountered error
            raise last_error

    except Exception as e:
        PolicyServer.log_request("anonymous", code, f"ERROR: {str(e)}")
        return jsonify({
            "error": "AI Analysis Failed",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting Bug Hunter server on http://127.0.0.1:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)
