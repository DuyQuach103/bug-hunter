---
name: analyze-java
description: Analyze Java code for bugs, security issues, and performance problems. Use when user submits Java code for debugging.
---

# Analyze Java Skill

## When to use
- User pastes Java code
- User asks "Find bugs in this Java code"
- User wants Java code analysis

## When NOT to use
- Code is not Java → use detect-language first

## Workflow
1. Read the Java code
2. Check for syntax errors:
   - Missing semicolons
   - Unclosed braces
   - Missing return statements
   - Incorrect method signatures
3. Check for logic errors:
   - Null pointer risks
   - Off-by-one in loops
   - Infinite loops
   - Incorrect type usage
4. Check for performance issues:
   - Unnecessary object creation
   - Inefficient loops
   - Missing StringBuilder for string concatenation
5. Check for security issues:
   - Hardcoded passwords
   - SQL injection risks
   - Unvalidated user input
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
  - Input: `System.out.println("Hello")` (missing semicolon)
  - Output: 🔴 ERROR: Line 1 - Missing semicolon → Add `;`
- **Example 2**:
  - Input: `String s = null; s.length();` (potential NullPointerException)
  - Output: 🔴 ERROR: Line 2 - Dereferencing null pointer `s` → Add null check `if (s != null)`
