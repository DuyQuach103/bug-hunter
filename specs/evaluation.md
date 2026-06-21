# Evaluation & Testing Specifications - Bug Hunter

This document details the LLM-as-Judge evaluation framework, test case datasets, and metrics used to assess the quality of Bug Hunter's analyses.

## Evaluation Architecture

The Bug Hunter test suite evaluates the accuracy and helpfulness of the debugging engine's outputs by running them against a set of reference buggy cases and grading them with a secondary judge LLM.

```
┌─────────────────┐
│  Test Runner    │
│ (run_tests.py)  │
└────────┬────────┘
         │
         ├─── (Loads 15 cases) ───> [test_cases.py]
         │
         ├─── (POST /debug) ──────> [Bug Hunter Service] ───> (Gets Report)
         │
         └─── (Scores Report) ────> [LLM Judge (judge.py)] ───> (1-10 Grades)
```

---

## 1. Test Dataset (`test_cases.py`)

The test suite consists of **15 distinct test cases** designed to cover a wide spectrum of code quality and programming issues:

| Category | Count | Description |
|----------|-------|-------------|
| **Syntax Errors** | 3 | Missing colons, unmatched parentheses, indentation errors. |
| **Logic Errors** | 3 | Off-by-one errors, division-by-zero, incorrect math equations. |
| **Performance Issues** | 3 | Unnecessary nested loops, database connection leaks, memory leaks. |
| **Security Risks** | 3 | Command injections, hardcoded passwords, SQL injections. |
| **Code Quality** | 2 | Clean code checking, formatting inconsistencies. |
| **Perfect Code** | 1 | Completely clean, optimal code that should receive 0 bug reports. |

---

## 2. LLM-as-Judge scoring (`judge.py`)

A secondary Gemini instance (`gemini-2.5-flash`) acts as an expert code reviewer to score the Bug Hunter analysis reports on four key dimensions:

1. **Accuracy (1–10)**: Did the analysis correctly identify the bugs that were actually in the code?
2. **Correctness (1–10)**: Are the proposed fixes and refactored code snippets correct and safe to run?
3. **Completeness (1–10)**: Did the analysis report all bugs, or did it miss anything crucial?
4. **Helpfulness (1–10)**: Are the suggestions, complexity estimates, and refactor tips useful to a developer?

The judge returns a structured JSON payload:
```json
{
  "accuracy": 9,
  "correctness": 8,
  "completeness": 9,
  "helpfulness": 10,
  "justification": "Detailed explanation of why these scores were assigned..."
}
```

---

## 3. Test Runner Pipeline (`run_tests.py`)

* **Execution Flow**:
  1. Calls the `/debug` endpoint for each test case.
  2. Compares returned bugs against `expected_bugs` declared in the test case.
  3. Passes the result to the LLM-as-Judge for scoring.
  4. Records pass/fail status (tests pass if LLM score averages $\ge 7.0$ and expected bugs are captured).
* **API Rate Limit Guarding**: Spaces API requests with dynamic backoff delays (e.g. 12s sleep between cases) to prevent hitting Gemini API quotas (`429 RESOURCE_EXHAUSTED`).
* **Reports Export**: Generates test summaries as `eval_report.json` and a formatted markdown table in `eval_report.md`.

---

## 4. Dashboard Integration

* **Triggering Evaluations**: Clicking the **Run Evaluation** button in the dashboard sends a request to `/eval`.
* **Rendering Metrics**: Once finished, it displays a summary (pass rate, total tests, average judge score) alongside status cards for each of the 15 test cases, providing direct insight into the debugger's performance.
