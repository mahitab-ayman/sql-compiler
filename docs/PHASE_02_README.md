# Phase 02: Syntax Analysis

## 📋 Overview

The Syntax Analyzer (Parser) is the second phase of the compiler. It takes the token stream from Phase 01 and constructs a hierarchical parse tree structure that represents the syntactic structure of the SQL statements according to the language grammar.

## 🎯 Objectives

1. Build parse tree from token stream
2. Validate syntax according to grammar rules
3. Detect and report syntax errors
4. Implement error recovery mechanisms
5. Generate ASCII and graphical tree visualizations

## 🔧 Implementation

### File: `parser.py`

### Parsing Technique

**Recursive Descent Parsing:**
- Top-down parsing approach
- One parsing function per grammar rule
- Clean and maintainable code structure
- Easy to modify and extend

### ParseTreeNode Class

```python
class ParseTreeNode:
    def __init__(self, node_type, value=None, children=None, line=None, column=None):
        self.node_type = node_type    # Type of node (STATEMENT, IDENTIFIER, etc.)
        self.value = value            # Value (for terminals)
        self.children = children      # List of child nodes
        self.line = line              # Line number
        self.column = column          # Column number
        self.data_type = None         # For Phase 03 (semantic analysis)
        self.symbol_ref = None        # For Phase 03 (semantic analysis)
```

### SyntaxAnalyzer Class

#### Main Methods

1. **`__init__(tokens)`**
   - Initialize parser with token list
   - Set up error tracking

2. **`parse()`**
   - Entry point for parsing
   - Returns parse tree root

3. **`get_parse_tree()`**
   - Returns the generated parse tree

4. **`get_errors()`**
   - Returns list of syntax errors

#### Parsing Methods (Grammar Rules)

- `parse_statement()` - Parse a complete SQL statement
- `parse_create_table()` - Parse CREATE TABLE statement
- `parse_insert()` - Parse INSERT INTO statement
- `parse_select()` - Parse SELECT statement
- `parse_update()` - Parse UPDATE statement
- `parse_delete()` - Parse DELETE statement
- `parse_where_clause()` - Parse WHERE conditions
- `parse_condition()` - Parse logical conditions
- `parse_expression()` - Parse expressions
- `parse_identifier()` - Parse identifiers
- `parse_value_list()` - Parse value lists

#### Helper Methods

- `current_token()` - Get current token
- `peek_token()` - Look ahead at next token
- `advance()` - Move to next token
- `match()` - Check if current token matches expected
- `consume()` - Consume token if it matches
- `report_error()` - Add syntax error to list
- `synchronize()` - Error recovery mechanism

## 📊 Grammar

### Complete Grammar Rules

```
program         → statement+

statement       → sql_statement ';'

sql_statement   → create_table | insert | select | update | delete

create_table    → 'CREATE' 'TABLE' identifier '(' column_list ')'
column_list     → column_def (',' column_def)*
column_def      → identifier data_type
data_type       → 'INT' | 'FLOAT' | 'TEXT'

insert          → 'INSERT' 'INTO' identifier 'VALUES' value_list
                | 'INSERT' 'INTO' identifier '(' identifier_list ')' 'VALUES' value_list
value_list      → '(' expression (',' expression)* ')'

select          → 'SELECT' select_list 'FROM' identifier where_clause?
select_list     → '*' | identifier_list
identifier_list → identifier (',' identifier)*

update          → 'UPDATE' identifier 'SET' assignment_list where_clause?
assignment_list → assignment (',' assignment)*
assignment      → identifier '=' expression

delete          → 'DELETE' 'FROM' identifier where_clause?

where_clause    → 'WHERE' condition

condition       → simple_condition (('AND' | 'OR') simple_condition)*
                | 'NOT' condition
                | '(' condition ')'

simple_condition→ identifier comparison_op expression
comparison_op   → '=' | '<' | '>' | '<=' | '>=' | '<>' | '!='

expression      → identifier | literal
literal         → INT_LITERAL | FLOAT_LITERAL | STRING_LITERAL
identifier      → IDENTIFIER
```

## 🌳 Parse Tree Structure

### Node Types

| Node Type | Description | Example |
|-----------|-------------|---------|
| `PROGRAM` | Root node | Contains all statements |
| `STATEMENT` | Statement wrapper | Contains SQL command + semicolon |
| `CREATE_TABLE` | CREATE TABLE node | Table creation |
| `INSERT` | INSERT INTO node | Data insertion |
| `SELECT` | SELECT node | Data query |
| `UPDATE` | UPDATE node | Data modification |
| `DELETE` | DELETE node | Data deletion |
| `IDENTIFIER` | Identifier node | Table/column names |
| `KEYWORD` | Keyword node | SQL keywords |
| `LITERAL` | Literal value | Numbers, strings |
| `OPERATOR` | Operator node | =, <, >, etc. |
| `DELIMITER` | Delimiter node | (, ), ,, ; |
| `WHERE_CLAUSE` | WHERE condition | Filtering conditions |
| `COMPARISON` | Comparison node | age > 18 |
| `ERROR` | Error node | Syntax errors |

### Example Parse Tree

**Input:**
```sql
CREATE TABLE Students (id INT, name TEXT);
```

**Parse Tree:**
```
PROGRAM
└── STATEMENT
    ├── CREATE_TABLE
    │   ├── KEYWORD (CREATE)
    │   ├── KEYWORD (TABLE)
    │   ├── IDENTIFIER (Students)
    │   ├── DELIMITER (()
    │   ├── COLUMN_LIST
    │   │   ├── COLUMN_DEFINITION
    │   │   │   ├── IDENTIFIER (id)
    │   │   │   └── DATA_TYPE (INT)
    │   │   ├── DELIMITER (,)
    │   │   └── COLUMN_DEFINITION
    │   │       ├── IDENTIFIER (name)
    │   │       └── DATA_TYPE (TEXT)
    │   └── DELIMITER ())
    └── SEMICOLON (;)
```

## 🔍 Features

### 1. Error Recovery

The parser implements **panic mode error recovery**:
- When error is detected, parser synchronizes to next statement
- Looks for semicolons or major keywords (CREATE, INSERT, SELECT, etc.)
- Continues parsing to find more errors

### 2. Error Detection

Detects the following syntax errors:
- Missing keywords (INTO, FROM, WHERE, etc.)
- Missing semicolons
- Unbalanced parentheses
- Missing table/column names
- Invalid statement structure
- Unexpected tokens

### 3. Detailed Error Messages

Errors include:
- Error type (Syntax Error)
- Descriptive message
- Line number
- Column number

Example:
```
Syntax Error: Expected KEYWORD 'INTO' but found IDENTIFIER 'Students' 
at line 5, column 8
```

### 4. No Cascade Errors

The parser avoids reporting duplicate/cascade errors:
- Uses `has_error()` method to check if node contains errors
- Skips semicolon check if statement already has errors
- Reports only unique, meaningful errors

## 📝 Example

### Complete Example

**Input:**
```sql
CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT
);

INSERT INTO Students VALUES (1, 'Alice', 20);
SELECT * FROM Students WHERE age > 18;
UPDATE Students SET age = 21 WHERE id = 1;
DELETE FROM Students WHERE age < 18;
```

**Parse Tree Output:**
```
PROGRAM
├── STATEMENT
│   ├── CREATE_TABLE
│   │   ├── KEYWORD (CREATE)
│   │   ├── KEYWORD (TABLE)
│   │   ├── IDENTIFIER (Students)
│   │   ├── DELIMITER (()
│   │   ├── COLUMN_LIST
│   │   │   ├── COLUMN_DEFINITION
│   │   │   │   ├── IDENTIFIER (id)
│   │   │   │   └── DATA_TYPE (INT)
│   │   │   ├── DELIMITER (,)
│   │   │   ├── COLUMN_DEFINITION
│   │   │   │   ├── IDENTIFIER (name)
│   │   │   │   └── DATA_TYPE (TEXT)
│   │   │   ├── DELIMITER (,)
│   │   │   └── COLUMN_DEFINITION
│   │   │       ├── IDENTIFIER (age)
│   │   │       └── DATA_TYPE (INT)
│   │   └── DELIMITER ())
│   └── SEMICOLON (;)
├── STATEMENT
│   ├── INSERT
│   │   ├── KEYWORD (INSERT)
│   │   ├── KEYWORD (INTO)
│   │   ├── IDENTIFIER (Students)
│   │   ├── KEYWORD (VALUES)
│   │   └── VALUE_LIST
│   │       ├── DELIMITER (()
│   │       ├── LITERAL (1) [type: INT]
│   │       ├── DELIMITER (,)
│   │       ├── LITERAL (Alice) [type: STRING]
│   │       ├── DELIMITER (,)
│   │       ├── LITERAL (20) [type: INT]
│   │       └── DELIMITER ())
│   └── SEMICOLON (;)
├── STATEMENT
│   ├── SELECT
│   │   ├── KEYWORD (SELECT)
│   │   ├── SELECT_LIST
│   │   │   └── OPERATOR (*)
│   │   ├── KEYWORD (FROM)
│   │   └── IDENTIFIER (Students)
│   │   └── WHERE_CLAUSE
│   │       ├── KEYWORD (WHERE)
│   │       └── COMPARISON
│   │           ├── IDENTIFIER (age)
│   │           ├── OPERATOR (>)
│   │           └── LITERAL (18) [type: INT]
│   └── SEMICOLON (;)
└── ... (more statements)
```

## 🚨 Error Handling

### Error Structure

```python
{
    'type': 'Syntax Error',
    'message': 'Expected FROM keyword but found Students',
    'line': 5,
    'column': 10
}
```

### Common Syntax Errors

1. **Missing Keywords:**
   ```sql
   INSERT Students VALUES (1, 'Alice');  -- Missing INTO
   SELECT * Students;                     -- Missing FROM
   ```

2. **Missing Semicolons:**
   ```sql
   INSERT INTO Students VALUES (1, 'Alice')  -- Missing ;
   SELECT * FROM Students;
   ```

3. **Unbalanced Parentheses:**
   ```sql
   CREATE TABLE Students (id INT;  -- Missing )
   ```

4. **Invalid Structure:**
   ```sql
   SELECT FROM Students WHERE;  -- Missing column list
   ```

## 🎨 Visualization

### ASCII Tree

The parser generates ASCII art visualization:

```
PROGRAM
+-- STATEMENT
|   +-- CREATE_TABLE
|   |   +-- KEYWORD (CREATE)
|   |   +-- KEYWORD (TABLE)
|   |   +-- IDENTIFIER (Students)
|   |   +-- DELIMITER (()
|   |   +-- COLUMN_LIST
|   |   |   +-- COLUMN_DEFINITION
|   |   |   |   +-- IDENTIFIER (id)
|   |   |   |   `-- DATA_TYPE (INT)
|   |   |   `-- ...
|   |   `-- DELIMITER ())
|   `-- SEMICOLON (;)
`-- ...
```

### Graphical Tree

The GUI provides color-coded graphical visualization:
- 🔵 Blue - PROGRAM, STATEMENT, KEYWORD
- 🟢 Green - INSERT
- 🟡 Yellow - SELECT
- 🟠 Orange - UPDATE
- 🔴 Red - DELETE
- 🟣 Purple - IDENTIFIER
- 🌸 Pink - LITERAL

## 🧪 Testing

### Test Cases

1. **CREATE TABLE:**
   ```sql
   CREATE TABLE Test (id INT, name TEXT);
   ```

2. **INSERT INTO:**
   ```sql
   INSERT INTO Test VALUES (1, 'Alice');
   ```

3. **SELECT:**
   ```sql
   SELECT * FROM Test;
   SELECT id, name FROM Test WHERE id = 1;
   ```

4. **UPDATE:**
   ```sql
   UPDATE Test SET name = 'Bob' WHERE id = 1;
   ```

5. **DELETE:**
   ```sql
   DELETE FROM Test WHERE id > 10;
   ```

6. **Complex WHERE:**
   ```sql
   SELECT * FROM Test WHERE (age > 18 AND age < 30) OR status = 'active';
   ```

### Running Tests

```python
from lexer import LexicalAnalyzer
from parser import SyntaxAnalyzer

source = """
CREATE TABLE Test (id INT);
SELECT * FROM Test;
"""

# Phase 01
lexer = LexicalAnalyzer(source)
lexer.tokenize()
tokens = lexer.get_tokens()

# Phase 02
parser = SyntaxAnalyzer(tokens)
parse_tree = parser.parse()
errors = parser.get_errors()

print(f"Parse tree: {parse_tree.to_string()}")
print(f"Errors: {len(errors)}")
```

## 📈 Performance

- **Time Complexity:** O(n) where n is the number of tokens
- **Space Complexity:** O(d) where d is the depth of parse tree

## 🔗 Next Phase

The parse tree generated by the Syntax Analyzer is passed to **Phase 03: Semantic Analyzer** for type checking and semantic validation.

[→ Go to Phase 03 Documentation](PHASE_03_README.md)

---

**Phase 02 Complete! ✅**
