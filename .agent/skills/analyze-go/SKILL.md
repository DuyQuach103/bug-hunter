---
name: analyze-go
description: Analyze Go code for bugs, security issues, and performance problems. Use when user submits Go code for debugging.
---

# Analyze Go Skill

## When to use
- User pastes Go code
- User asks "Find bugs in this Go code"

## When NOT to use
- Code is not Go → use detect-language first

## Workflow
1. Read the Go code
2. Check for syntax errors:
   - Missing imports
   - Type mismatches
   - Incorrect error handling
3. Check for logic errors:
   - Nil pointer dereference
   - Missing error checks
   - Race conditions
4. Check for performance issues:
   - Inefficient memory allocation
   - Blocking operations
5. Check for security issues:
   - Hardcoded secrets
   - Unsafe package usage
6. Generate report

## Output format
🔴 ERRORS (SYNTAX & LOGIC)
Line X: [problem] → [fix]
🟡 WARNINGS (PERFORMANCE & SECURITY)
Line X: [problem] → [fix]
💚 CODE STRENGTHS
[strength 1]
💡 RECOMMENDATIONS
[recommendation 1]
⏱️ TIME COMPLEXITY: O(?)
📦 SPACE COMPLEXITY: O(?)

## Examples
- **Example 1**:
  - Input: `f, _ := os.Open("file.txt")` (ignored error variable)
  - Output: 🟡 WARNING: Line 1 - Ignored error value returned from `os.Open` → Handle the error variable instead of ignoring it with `_`
- **Example 2**:
  - Input: `var p *int; *p = 5` (nil pointer dereference)
  - Output: 🔴 ERROR: Line 2 - Nil pointer dereference on `p` → Initialize `p` using `new(int)` or assign it a valid address before dereferencing
