---
name: analyze-javascript
description: Analyze JavaScript code for bugs, security issues, and performance problems. Use when user submits JavaScript code for debugging.
---

# Analyze JavaScript Skill

## When to use
- User pastes JavaScript code
- User asks "Find bugs in this JavaScript code"

## When NOT to use
- Code is not JavaScript → use detect-language first

## Workflow
1. Read the JavaScript code
2. Check for syntax errors:
   - Missing brackets or parentheses
   - Missing semicolons
   - Variable scope issues
3. Check for logic errors:
   - Undefined variables
   - Type coercion issues
   - Async/await errors
4. Check for performance issues:
   - Inefficient DOM manipulation
   - Memory leaks
   - Reflow issues
5. Check for security issues:
   - XSS risks
   - Unsafe eval()
   - Hardcoded secrets
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
  - Input: `let x = ;` (syntax error)
  - Output: 🔴 ERROR: Line 1 - Unexpected token `;` → Assign a valid value
- **Example 2**:
  - Input: `element.innerHTML = userInput;` (XSS vulnerability)
  - Output: 🟡 WARNING: Line 1 - DOM XSS risk via innerHTML → Use textContent or sanitize inputs
