---
name: analyze-cpp
description: Analyze C++ code for bugs, security issues, and performance problems. Use when user submits C++ code for debugging.
---

# Analyze C++ Skill

## When to use
- User pastes C++ code
- User asks "Find bugs in this C++ code"

## When NOT to use
- Code is not C++ → use detect-language first

## Workflow
1. Read the C++ code
2. Check for syntax errors:
   - Missing semicolons
   - Incorrect includes
   - Type mismatches
3. Check for logic errors:
   - Memory leaks
   - Dangling pointers
   - Buffer overflows
   - Uninitialized variables
4. Check for performance issues:
   - Inefficient copying
   - Missing move semantics
5. Check for security issues:
   - Buffer overflow risks
   - Use-after-free
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
  - Input: `int* p = new int[10];` (potential memory leak if not deleted)
  - Output: 🟡 WARNING: Line 1 - Potential memory leak. Allocated pointer `p` is never deleted → Add `delete[] p;` or use smart pointers like `std::unique_ptr`
- **Example 2**:
  - Input: `cout << "Hello"` (missing semicolon)
  - Output: 🔴 ERROR: Line 1 - Missing semicolon after statement → Add `;`
