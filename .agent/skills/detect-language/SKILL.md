---
name: detect-language
description: Detect programming language from code snippets. Use when the language is unknown or user didn't specify it.
---

# Detect Language Skill

## When to use
- User pastes code without specifying language
- User asks "What language is this?"
- Before analyzing code, need to know the language

## When NOT to use
- User explicitly states the language
- The file extension is clear (.py, .java, .js)

## Detection Rules

### Python
- `def` keyword
- `print()` function
- No semicolons
- Colon after `if`/`for`/`def`
- Indentation for blocks
- `.py` extension

### Java
- `public class`
- `System.out.println()`
- Semicolons
- Braces `{ }`
- `String[] args`
- `.java` extension

### JavaScript
- `function` or `=>` arrow
- `console.log()`
- `var`/`let`/`const`
- `.js` extension

### C++
- `#include`
- `std::cout`
- `::` scope resolution
- `->` pointers
- `.cpp` extension

### Go
- `package` declaration
- `func` keyword
- `:=` assignment
- `err != nil`
- `.go` extension

### Rust
- `fn` keyword
- `let mut`
- `println!` macro
- `.rs` extension

## Output format
Detected: [Language]
Confidence: [XX]%
Evidence: [key features found]

## Examples
- **Example 1**:
  - Input: `print("Hello")`
  - Output: Python (95% confidence) - print() function detected
- **Example 2**:
  - Input: `fn main() { println!("Hello"); }`
  - Output: Rust (99% confidence) - fn keyword and println! macro detected
