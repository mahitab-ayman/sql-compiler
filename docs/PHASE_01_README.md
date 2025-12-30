# Phase 01: Lexical Analysis

## 📋 Overview

The Lexical Analyzer (Lexer) is the first phase of the compiler. It reads the source code character by character and converts it into a sequence of tokens. Each token represents a meaningful unit in the language (keywords, identifiers, operators, literals, etc.).

## 🎯 Objectives

1. Tokenize SQL-like source code
2. Identify and classify different token types
3. Track line and column numbers for error reporting
4. Detect and report lexical errors
5. Filter out comments and whitespace

## 🔧 Implementation

### File: `lexer.py`

### Token Types

| Type | Description | Examples |
|------|-------------|----------|
| `KEYWORD` | Reserved words | CREATE, INSERT, SELECT, UPDATE, DELETE, TABLE, INTO, VALUES, FROM, WHERE, SET, AND, OR, NOT |
| `IDENTIFIER` | User-defined names | student_id, tableName, age |
| `INT_LITERAL` | Integer numbers | 42, -10, 0, 1234 |
| `FLOAT_LITERAL` | Floating-point numbers | 3.14, -0.5, 2.0 |
| `STRING_LITERAL` | Text strings | 'Alice', 'Hello World' |
| `OPERATOR` | Comparison/arithmetic ops | =, <, >, <=, >=, <>, !=, * |
| `DELIMITER` | Punctuation | (, ), ,, ; |
| `COMMENT` | Single-line comments | -- This is a comment |
| `EOF` | End of file marker | (automatic) |

### Token Class

```python
class Token:
    def __init__(self, token_type, lexeme, line, column):
        self.token_type = token_type  # Type of token
        self.lexeme = lexeme          # Actual text
        self.line = line              # Line number
        self.column = column          # Column number
```

### LexicalAnalyzer Class

#### Main Methods

1. **`__init__(source_code)`**
   - Initialize the lexer with source code
   - Set up position tracking

2. **`tokenize()`**
   - Main tokenization loop
   - Processes entire source code
   - Returns list of tokens

3. **`get_tokens()`**
   - Returns the list of generated tokens

4. **`get_errors()`**
   - Returns list of lexical errors

#### Helper Methods

- `peek()` - Look ahead at next character without consuming
- `advance()` - Move to next character
- `skip_whitespace()` - Skip spaces, tabs, newlines
- `skip_comment()` - Skip single-line comments (-- ...)
- `read_identifier()` - Read identifier or keyword
- `read_number()` - Read integer or float literal
- `read_string()` - Read string literal (quoted text)
- `is_keyword()` - Check if identifier is a keyword

## 📊 Algorithm

```
1. Initialize position to start of source code
2. While not at end of file:
   a. Skip whitespace and comments
   b. Identify current character type:
      - Letter/underscore → Read identifier/keyword
      - Digit → Read number (int or float)
      - Quote → Read string literal
      - Operator character → Read operator
      - Delimiter character → Read delimiter
      - Invalid character → Report error
   c. Create token and add to list
3. Add EOF token
4. Return token list
```

## 🔍 Features

### 1. Keyword Recognition

The lexer recognizes the following keywords:
- **DDL:** CREATE, TABLE
- **DML:** INSERT, INTO, VALUES, SELECT, FROM, WHERE, UPDATE, SET, DELETE
- **Logical:** AND, OR, NOT
- **Data Types:** INT, FLOAT, TEXT

### 2. Number Parsing

- **Integers:** `42`, `-10`, `0`
- **Floats:** `3.14`, `-0.5`, `2.0`
- Automatically distinguishes between INT and FLOAT based on decimal point

### 3. String Parsing

- Single-quoted strings: `'Alice'`, `'Hello World'`
- Handles spaces and special characters inside strings
- Detects unclosed string errors

### 4. Comment Handling

- Single-line comments start with `--`
- Comments extend to end of line
- Ignored during tokenization

### 5. Error Detection

Detects the following lexical errors:
- Invalid characters
- Unclosed string literals
- Malformed numbers

## 📝 Example

### Input (SQL Code)

```sql
-- Create a table
CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT
);

INSERT INTO Students VALUES (1, 'Alice', 20);
SELECT * FROM Students WHERE age > 18;
```

### Output (Tokens)

```
Token(COMMENT, '-- Create a table', 1, 1)
Token(KEYWORD, 'CREATE', 2, 1)
Token(KEYWORD, 'TABLE', 2, 8)
Token(IDENTIFIER, 'Students', 2, 14)
Token(DELIMITER, '(', 2, 23)
Token(IDENTIFIER, 'id', 3, 5)
Token(KEYWORD, 'INT', 3, 8)
Token(DELIMITER, ',', 3, 11)
Token(IDENTIFIER, 'name', 4, 5)
Token(KEYWORD, 'TEXT', 4, 10)
Token(DELIMITER, ',', 4, 14)
Token(IDENTIFIER, 'age', 5, 5)
Token(KEYWORD, 'INT', 5, 9)
Token(DELIMITER, ')', 6, 1)
Token(DELIMITER, ';', 6, 2)
Token(KEYWORD, 'INSERT', 8, 1)
Token(KEYWORD, 'INTO', 8, 8)
Token(IDENTIFIER, 'Students', 8, 13)
Token(KEYWORD, 'VALUES', 8, 22)
Token(DELIMITER, '(', 8, 29)
Token(INT_LITERAL, '1', 8, 30)
Token(DELIMITER, ',', 8, 31)
Token(STRING_LITERAL, 'Alice', 8, 33)
Token(DELIMITER, ',', 8, 40)
Token(INT_LITERAL, '20', 8, 42)
Token(DELIMITER, ')', 8, 44)
Token(DELIMITER, ';', 8, 45)
Token(KEYWORD, 'SELECT', 9, 1)
Token(OPERATOR, '*', 9, 8)
Token(KEYWORD, 'FROM', 9, 10)
Token(IDENTIFIER, 'Students', 9, 15)
Token(KEYWORD, 'WHERE', 9, 24)
Token(IDENTIFIER, 'age', 9, 30)
Token(OPERATOR, '>', 9, 34)
Token(INT_LITERAL, '18', 9, 36)
Token(DELIMITER, ';', 9, 38)
Token(EOF, '', 9, 39)
```

## 🚨 Error Handling

### Error Structure

```python
{
    'type': 'LEXICAL_ERROR',
    'message': 'Error description',
    'line': line_number,
    'column': column_number
}
```

### Example Errors

1. **Invalid Character:**
   ```
   Lexical Error: Invalid character '@' at line 5, column 10
   ```

2. **Unclosed String:**
   ```
   Lexical Error: Unclosed string literal at line 3, column 15
   ```

## 🧪 Testing

### Test Cases

1. **Keywords:**
   ```sql
   CREATE TABLE SELECT INSERT UPDATE DELETE
   ```

2. **Identifiers:**
   ```sql
   student_id tableName age_123 _private
   ```

3. **Numbers:**
   ```sql
   42 -10 3.14 -0.5 0 0.0
   ```

4. **Strings:**
   ```sql
   'Alice' 'Hello World' 'It''s working'
   ```

5. **Operators:**
   ```sql
   = < > <= >= <> != *
   ```

6. **Comments:**
   ```sql
   -- This is a comment
   SELECT * FROM Students; -- Another comment
   ```

### Running Tests

```python
from lexer import LexicalAnalyzer

# Test case
source = """
CREATE TABLE Test (id INT);
INSERT INTO Test VALUES (1);
"""

lexer = LexicalAnalyzer(source)
lexer.tokenize()
tokens = lexer.get_tokens()
errors = lexer.get_errors()

print(f"Tokens: {len(tokens)}")
print(f"Errors: {len(errors)}")

for token in tokens:
    print(token)
```

## 📈 Performance

- **Time Complexity:** O(n) where n is the length of source code
- **Space Complexity:** O(m) where m is the number of tokens

## 🔗 Next Phase

The tokens generated by the Lexical Analyzer are passed to **Phase 02: Syntax Analyzer** for parse tree generation.

[→ Go to Phase 02 Documentation](PHASE_02_README.md)

---

**Phase 01 Complete! ✅**
