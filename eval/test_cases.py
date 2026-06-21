# Bug Hunter Evaluation Test Suite

TEST_CASES = [
    # Category 1: Syntax Errors (3 cases)
    {
        "id": "TC001",
        "category": "syntax_error",
        "name": "Missing colon in function definition",
        "code": "def greet(name)\n    print('Hello')",
        "expected_bugs": ["Missing colon"],
        "severity": "high"
    },
    {
        "id": "TC002",
        "category": "syntax_error",
        "name": "Wrong indentation in block",
        "code": "def greet(name):\nprint('Hello')",
        "expected_bugs": ["IndentationError", "Wrong indentation"],
        "severity": "high"
    },
    {
        "id": "TC003",
        "category": "syntax_error",
        "name": "Missing closing parenthesis",
        "code": "print('Hello'",
        "expected_bugs": ["Missing parenthesis", "SyntaxError"],
        "severity": "high"
    },

    # Category 2: Logic Errors (3 cases)
    {
        "id": "TC004",
        "category": "logic_error",
        "name": "Wrong comparison in logical condition",
        "code": "def is_adult(age):\n    if age == 18 or 19:\n        return True\n    return False",
        "expected_bugs": ["Wrong comparison operator", "Incorrect logical expression", "always evaluates to True"],
        "severity": "medium"
    },
    {
        "id": "TC005",
        "category": "logic_error",
        "name": "Off-by-one in index boundary check",
        "code": "def get_element(lst, index):\n    if index <= len(lst):\n        return lst[index]\n    return None",
        "expected_bugs": ["Off-by-one error", "IndexError risk", "Index out of bounds"],
        "severity": "medium"
    },
    {
        "id": "TC006",
        "category": "logic_error",
        "name": "Infinite loop due to constant condition",
        "code": "def count_down(n):\n    while n > 0:\n        print(n)\n        # missing decrement",
        "expected_bugs": ["Infinite loop", "Missing state update"],
        "severity": "high"
    },

    # Category 3: Performance Issues (2 cases)
    {
        "id": "TC007",
        "category": "performance",
        "name": "O(n^2) list membership check in loop",
        "code": "def find_common(lst1, lst2):\n    common = []\n    for item in lst1:\n        if item in lst2:\n            common.append(item)\n    return common",
        "expected_bugs": ["O(n^2) complexity", "Inefficient membership lookup", "Use set for optimization"],
        "severity": "medium"
    },
    {
        "id": "TC008",
        "category": "performance",
        "name": "Inefficient string concatenation in loop",
        "code": "def join_strings(words):\n    result = ''\n    for word in words:\n        result += word\n    return result",
        "expected_bugs": ["Inefficient string concatenation", "Use join instead"],
        "severity": "low"
    },

    # Category 4: Security Issues (2 cases)
    {
        "id": "TC009",
        "category": "security",
        "name": "Hardcoded sensitive credentials",
        "code": "def login():\n    admin_password = 'SuperSecretPassword123!'\n    return admin_password",
        "expected_bugs": ["Hardcoded credentials", "Sensitive data exposure", "Hardcoded password"],
        "severity": "high"
    },
    {
        "id": "TC010",
        "category": "security",
        "name": "SQL injection vulnerability",
        "code": "def get_user_profile(db_cursor, username):\n    query = f\"SELECT * FROM users WHERE username = '{username}'\"\n    db_cursor.execute(query)\n    return db_cursor.fetchone()",
        "expected_bugs": ["SQL injection risk", "Unsanitized input in query", "Use parameterized query"],
        "severity": "high"
    },

    # Category 5: Code Quality (3 cases)
    {
        "id": "TC011",
        "category": "code_quality",
        "name": "Unused imports in module",
        "code": "import os\nimport sys\nimport math\n\ndef calculate_square(x):\n    return x * x",
        "expected_bugs": ["Unused imports", "Redundant imports"],
        "severity": "low"
    },
    {
        "id": "TC012",
        "category": "code_quality",
        "name": "Function with too many arguments",
        "code": "def register_user(first_name, last_name, email, age, gender, address, city, country, postal_code, phone):\n    pass",
        "expected_bugs": ["Too many arguments", "High parameter count"],
        "severity": "low"
    },
    {
        "id": "TC013",
        "category": "code_quality",
        "name": "Excessively long function violating single responsibility",
        "code": "def process_transaction(data):\n    # step 1: parse data\n    parsed = {}\n    for pair in data.split('&'):\n        k, v = pair.split('=')\n        parsed[k] = v\n    # step 2: validate fields\n    if 'amount' not in parsed or 'id' not in parsed:\n        return False\n    # step 3: format database record\n    record = {'tx_id': parsed['id'], 'amount': float(parsed['amount'])}\n    # step 4: print log message\n    print(\'Log:\', record)\n    # step 5: send confirmation email\n    print('Sending email to', parsed.get('email'))\n    # step 6: print audit log\n    print('Transaction processed successfully')\n    return True",
        "expected_bugs": ["Function too long", "Violates single responsibility principle"],
        "severity": "medium"
    },

    # Category 6: Perfect Code (2 cases)
    {
        "id": "TC014",
        "category": "perfect",
        "name": "Correct binary search implementation",
        "code": "def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
        "expected_bugs": [],
        "severity": "none"
    },
    {
        "id": "TC015",
        "category": "perfect",
        "name": "Clean utility function with docstring",
        "code": "def kelvin_to_celsius(kelvin: float) -> float:\n    \"\"\"Converts temperature from Kelvin to Celsius.\"\"\"\n    if kelvin < 0.0:\n        raise ValueError('Temperature below absolute zero is impossible')\n    return kelvin - 273.15",
        "expected_bugs": [],
        "severity": "none"
    }
]
