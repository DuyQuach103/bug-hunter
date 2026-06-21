---
name: analyze-python
description: Analyze Python code for bugs, security issues, and performance problems. Use when user submits Python code for debugging.
---

# Analyze Python Skill

## When to use
- User pastes Python code
- User asks "Find bugs in this Python code"
- User wants Python code analysis

## When NOT to use
- Code is not Python → use detect-language first
- User asks to convert code → use convert-code skill

## Workflow
1. Read the Python code
2. Check for syntax errors:
   - Missing colons after if/for/def/class
   - Incorrect indentation
   - Unclosed parentheses or quotes
   - Missing imports
3. Check for logic errors:
   - Using `=` instead of `==` in conditions
   - Off-by-one errors in loops
   - Infinite loop conditions
   - Variable scope issues
4. Check for performance issues:
   - O(n²) where O(n) is possible
   - Inefficient string concatenation in loops
   - Using list instead of set for membership tests
   - Unnecessary nested loops
5. Check for security issues:
   - Hardcoded passwords or API keys
   - Using eval() or exec() on user input
   - SQL injection risks
   - Subprocess calls without validation
6. Generate report with:
   - 🔴 Errors (must fix)
   - 🟡 Warnings (should fix)
   - 💚 Strengths (what's good)
   - 💡 Recommendations (how to improve)
   - ⏱️ Time Complexity
   - 📦 Space Complexity

## Output format
🔴 ERRORS (SYNTAX & LOGIC)
Line X: [problem] → [fix]
🟡 WARNINGS (PERFORMANCE & SECURITY)
Line X: [problem] → [fix]
💚 CODE STRENGTHS
[strength 1]
[strength 2]
💡 RECOMMENDATIONS
[recommendation 1]
[recommendation 2]
⏱️ TIME COMPLEXITY: O(?)
📦 SPACE COMPLEXITY: O(?)

## Examples
- **Example 1**:
  - Input: `print("Hello"` (missing closing parenthesis)
  - Output: 🔴 ERROR: Line 1 - Missing closing parenthesis → Add `)`
- **Example 2**:
  - Input: `if x = 5:` (assignment instead of comparison)
  - Output: 🔴 ERROR: Line 1 - Using `=` instead of `==` → Change to `if x == 5:`
