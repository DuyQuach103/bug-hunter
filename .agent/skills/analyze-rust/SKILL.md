---
name: analyze-rust
description: Analyze Rust code for bugs, security issues, and performance problems. Use when user submits Rust code for debugging.
---

# Analyze Rust Skill

## When to use
- User pastes Rust code
- User asks "Find bugs in this Rust code"

## When NOT to use
- Code is not Rust → use detect-language first

## Workflow
1. Read the Rust code
2. Check for syntax errors:
   - Missing semicolons
   - Incorrect lifetimes
   - Type mismatches
3. Check for logic errors:
   - Unwrap on Option/Result
   - Borrow checker violations
   - Panic risks
4. Check for performance issues:
   - Inefficient allocations
   - Cloning instead of borrowing
5. Check for security issues:
   - Unsafe code blocks
   - Integer overflow risks
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
  - Input: `let val = opt.unwrap();` (unwrap on option risk)
  - Output: 🟡 WARNING: Line 1 - Calling `.unwrap()` can cause panic if `opt` is `None` → Use `match`, `if let`, or `.unwrap_or()` to handle missing values safely
- **Example 2**:
  - Input: `let s = "hello"; let y = s.clone();` (unnecessary clone)
  - Output: 💡 RECOMMENDATION: Line 1 - Unnecessary cloning of shared string reference → Borrow it directly
