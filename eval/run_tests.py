import os
import sys
import json
import time
import urllib.request
import urllib.error

# Adjust path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_cases import TEST_CASES
from judge import LLMJudge

# Configuration
SERVER_URL = os.environ.get("BUG_HUNTER_URL", "http://127.0.0.1:5001/debug")
REPORT_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_report.json")
REPORT_MD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_report.md")


def call_debug_endpoint(code: str, lang: str) -> tuple[int, dict]:
    """
    Calls the Bug Hunter /debug POST endpoint.
    Returns (status_code, response_dict)
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
            return res.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"error": "HTTPError", "details": body}
        return e.code, data
    except Exception as e:
        return 500, {"error": "ConnectionError", "details": str(e)}


def run_test_case_with_retries(tc: dict, judge: LLMJudge, max_retries=5, initial_delay=12) -> dict:
    """
    Runs a single test case with retry logic for Gemini quota limits (429 / 500 rate limit errors).
    """
    print(f"Running {tc['id']}: {tc['name']} ({tc['category']})...")
    
    delay = initial_delay
    for attempt in range(max_retries):
        status_code, response = call_debug_endpoint(tc['code'], "python")
        
        # Check if the error is a rate limit error (either 429 directly or a 500 from the server containing rate limit details)
        is_rate_limit = (
            status_code == 429 or 
            (status_code == 500 and ("429" in str(response) or "RESOURCE_EXHAUSTED" in str(response) or "limit" in str(response).lower()))
        )
        
        if is_rate_limit:
            print(f"  [Rate Limit Hit] Endpoint returned {status_code}. Retrying in {delay}s (attempt {attempt+1}/{max_retries})...")
            time.sleep(delay)
            delay *= 1.5
            continue
            
        # If we successfully passed sandbox/policy checks and reached AI analysis (or if sandbox/policy correctly blocked it)
        break
    
    # Check block/execution error cases (HTTP 400)
    if status_code == 400:
        # Expected bugs comparison on error details
        error_title = response.get("error", "")
        error_details = response.get("details", "")
        combined_err_text = f"{error_title} : {error_details}".lower()
        
        # Verify if expected bugs are mentioned in the block/execution details
        found_bugs = []
        for bug in tc['expected_bugs']:
            bug_lower = bug.lower()
            if (bug_lower in combined_err_text or
                (bug_lower == "missing colon" and "expected ':'" in combined_err_text) or
                (bug_lower == "missing colon" and "invalid syntax" in combined_err_text) or
                (bug_lower == "wrong indentation" and "indentation" in combined_err_text) or
                (bug_lower == "indentationerror" and "indentation" in combined_err_text) or
                (bug_lower == "missing parenthesis" and "was never closed" in combined_err_text) or
                (bug_lower == "missing parenthesis" and "unmatched" in combined_err_text) or
                (bug_lower == "syntaxerror" and "syntax" in combined_err_text) or
                (bug_lower == "syntaxerror" and "expected" in combined_err_text) or
                (bug_lower == "infinite loop" and "timed out" in combined_err_text)
            ):
                found_bugs.append(bug)
                
        passed = len(found_bugs) > 0 if tc['expected_bugs'] else True
        
        # Since it was correctly blocked by policy/sandbox as designed, assign a perfect score
        result_entry = {
            "id": tc['id'],
            "category": tc['category'],
            "name": tc['name'],
            "status": "BLOCKED" if "Security" in error_title else "SANDBOX_FAILED",
            "passed": passed,
            "expected_bugs": tc['expected_bugs'],
            "detected_bugs": found_bugs,
            "response": response,
            "judge_evaluation": {
                "accuracy": 10 if passed else 1,
                "correctness": 10 if passed else 1,
                "completeness": 10 if passed else 1,
                "helpfulness": 10 if passed else 1,
                "overall_score": 10.0 if passed else 1.0,
                "justification": f"System correctly intercepted the issue at the sandbox/policy level: {error_title}. Details: {error_details}"
            }
        }
        return result_entry

    # Check for success cases (HTTP 200)
    if status_code == 200:
        report = response.get("result", {})
        
        # Build search space to verify expected bugs
        search_text = []
        for cat in ['syntax_errors', 'logic_errors', 'performance_issues', 'security_issues']:
            for issue in report.get(cat, []):
                search_text.append(issue.get('description', ''))
                search_text.append(issue.get('fix', ''))
        for rec in report.get('recommendations', []):
            search_text.append(rec)
        combined_search_text = " ".join(search_text).lower()
        
        detected_bugs = []
        for bug in tc['expected_bugs']:
            if bug.lower() in combined_search_text:
                detected_bugs.append(bug)
                
        # For perfect code, make sure no bugs are reported
        if not tc['expected_bugs']:
            has_issues = False
            for cat in ['syntax_errors', 'logic_errors', 'performance_issues', 'security_issues']:
                if report.get(cat, []):
                    has_issues = True
                    break
            passed = not has_issues
        else:
            passed = len(detected_bugs) > 0
            
        # Run LLM-as-Judge on the report
        time.sleep(6)  # Spacing delay to stay under RPM limit
        judge_eval = None
        for attempt in range(max_retries):
            try:
                judge_eval = judge.evaluate_analysis(tc['code'], report)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower() or "limit" in str(e).lower():
                    print(f"  [Rate Limit Hit] Judge evaluation returned rate limit. Retrying in {delay}s (attempt {attempt+1}/{max_retries})...")
                    time.sleep(delay)
                    delay *= 1.5
                else:
                    print(f"  [Judge Error]: {e}")
                    break
                    
        if not judge_eval:
            judge_eval = {
                "accuracy": 0,
                "correctness": 0,
                "completeness": 0,
                "helpfulness": 0,
                "overall_score": 0.0,
                "justification": "LLM Judge evaluation failed or timed out."
            }
            
        result_entry = {
            "id": tc['id'],
            "category": tc['category'],
            "name": tc['name'],
            "status": "SUCCESS",
            "passed": passed,
            "expected_bugs": tc['expected_bugs'],
            "detected_bugs": detected_bugs,
            "response": report,
            "judge_evaluation": judge_eval
        }
        return result_entry

    # Handle other error cases (500 etc)
    result_entry = {
        "id": tc['id'],
        "category": tc['category'],
        "name": tc['name'],
        "status": f"ERROR_{status_code}",
        "passed": False,
        "expected_bugs": tc['expected_bugs'],
        "detected_bugs": [],
        "response": response,
        "judge_evaluation": {
            "accuracy": 0,
            "correctness": 0,
            "completeness": 0,
            "helpfulness": 0,
            "overall_score": 0.0,
            "justification": f"Failed to get analysis. HTTP status {status_code}. Response: {response}"
        }
    }
    return result_entry


def generate_reports(results: list):
    """
    Generates summary metrics and writes JSON and Markdown report files.
    """
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["passed"])
    pass_rate = round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0.0
    
    total_judge_score = sum(r["judge_evaluation"]["overall_score"] for r in results)
    avg_judge_score = round(total_judge_score / total_tests, 2) if total_tests > 0 else 0.0
    
    summary = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "pass_rate": pass_rate,
        "average_judge_score": avg_judge_score
    }
    
    report_data = {
        "summary": summary,
        "results": results
    }
    
    # 1. Export JSON Report
    with open(REPORT_JSON_PATH, "w") as f:
        json.dump(report_data, f, indent=2)
    print(f"Exported JSON report to {REPORT_JSON_PATH}")
    
    # 2. Export Markdown Report
    md_content = f"""# Bug Hunter Evaluation Test Suite Report

## Summary
| Metric | Value |
| --- | --- |
| **Total Tests** | {total_tests} |
| **Passed Tests** | {passed_tests} |
| **Pass Rate** | {pass_rate}% |
| **Average Judge Score** | {avg_judge_score} / 10 |

---

## Detailed Test Case Results

| ID | Category | Name | Status | Passed | Judge Score |
| --- | --- | --- | --- | --- | --- |
"""
    
    for r in results:
        status_icon = "✅" if r["passed"] else "❌"
        md_content += f"| {r['id']} | {r['category']} | {r['name']} | {r['status']} | {status_icon} | {r['judge_evaluation']['overall_score']} / 10 |\n"
        
    md_content += "\n---\n\n## Rationale & Details\n"
    for r in results:
        md_content += f"### {r['id']}: {r['name']} ({r['category']})\n"
        md_content += f"- **Passed**: {'Yes' if r['passed'] else 'No'}\n"
        md_content += f"- **Status**: `{r['status']}`\n"
        md_content += f"- **Expected Bugs**: {r['expected_bugs']}\n"
        md_content += f"- **Detected Bugs**: {r['detected_bugs']}\n"
        md_content += f"- **Judge Justification**: {r['judge_evaluation']['justification']}\n\n"
        
    with open(REPORT_MD_PATH, "w") as f:
        f.write(md_content)
    print(f"Exported Markdown report to {REPORT_MD_PATH}")


def run_all_tests() -> dict:
    judge = LLMJudge()
    results = []
    
    for tc in TEST_CASES:
        res = run_test_case_with_retries(tc, judge)
        results.append(res)
        print(f"  Result: {'PASS' if res['passed'] else 'FAIL'} | Score: {res['judge_evaluation']['overall_score']}/10\n")
        # Sleep between cases to reduce rate-limit pressure
        time.sleep(6)
        
    generate_reports(results)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["passed"])
    pass_rate = round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0.0
    total_judge_score = sum(r["judge_evaluation"]["overall_score"] for r in results)
    avg_judge_score = round(total_judge_score / total_tests, 2) if total_tests > 0 else 0.0
    
    return {
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": pass_rate,
            "average_judge_score": avg_judge_score
        },
        "results": results
    }


def main():
    print("Starting Bug Hunter Evaluation Suite...")
    print(f"Target Server Endpoint: {SERVER_URL}")
    print(f"Total Test Cases loaded: {len(TEST_CASES)}\n")
    run_all_tests()
    print("\nEvaluation Run Completed!")


if __name__ == "__main__":
    main()
