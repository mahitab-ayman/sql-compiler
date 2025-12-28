# Phase 03: Semantic Analysis

## 📋 Overview

The Semantic Analyzer is the third and final phase of the compiler. It performs semantic validation on the parse tree generated in Phase 02, ensuring that the SQL statements are not only syntactically correct but also semantically meaningful. This includes type checking, symbol table management, and validation of identifier references.

## 🎯 Objectives

1. Build and manage symbol table for tables and columns
2. Verify table and column existence
3. Perform type checking on INSERT statements
4. Validate type compatibility in WHERE clauses
5. Prevent table redeclaration
6. Annotate parse tree with semantic information
7. Report semantic errors with detailed messages

## 🔧 Implementation

### File: `semantic.py`

### SymbolTable Class

Manages all declared tables and their column information.

```python
class SymbolTable:
    def __init__(self):
        self.tables = {}  # {table_name: {column_name: data_type}}

    def add_table(table_name, columns):
        """Add a table with its columns"""

    def table_exists(table_name):
        """Check if table exists"""

    def get_table_columns(table_name):
        """Get all columns for a table"""

    def get_column_type(table_name, column_name):
        """Get data type of specific column"""
```

### SemanticAnalyzer Class

Performs semantic validation and builds annotated parse tree.

#### Main Methods

1. **`__init__(parse_tree)`**
   - Initialize with parse tree from Phase 02
   - Create empty symbol table

2. **`analyze()`**
   - Entry point for semantic analysis
   - Returns True if successful, False otherwise

3. **`get_symbol_table()`**
   - Returns the symbol table

4. **`get_errors()`**
   - Returns list of semantic errors

5. **`get_success_message()`**
   - Returns success/failure message

6. **`get_results()`**
   - Returns complete analysis results

#### Analysis Methods

- `_analyze_node(node)` - Recursively analyze parse tree nodes
- `_analyze_create_table(node, annotated)` - Validate CREATE TABLE
- `_analyze_insert(node, annotated)` - Validate INSERT INTO
- `_analyze_select(node, annotated)` - Validate SELECT
- `_analyze_update(node, annotated)` - Validate UPDATE
- `_analyze_delete(node, annotated)` - Validate DELETE
- `_analyze_where_clause(where_node, table_name)` - Validate WHERE
- `_analyze_comparison(comp_node, table_name)` - Validate comparisons

#### Helper Methods

- `_extract_columns_from_list(column_list_node)` - Extract column definitions
- `_extract_values(value_list_node)` - Extract INSERT values
- `_types_compatible(expected, actual)` - Check type compatibility
- `_infer_type(value)` - Infer data type from literal value
- `add_error(message, line, column)` - Add semantic error

## 📊 Semantic Rules

### 1. Table Existence Verification

**Rule:** Any table referenced must exist in symbol table.

**Applies to:**
- INSERT INTO table_name
- SELECT FROM table_name
- UPDATE table_name
- DELETE FROM table_name

**Example Error:**
```sql
SELECT * FROM NonExistentTable;
```
```
Semantic Error: Table 'NonExistentTable' does not exist at line 1, column 15
```

### 2. Column Existence Verification

**Rule:** Any column referenced must exist in the table.

**Applies to:**
- SELECT column_name
- UPDATE SET column_name = value
- WHERE column_name = value

**Example Error:**
```sql
SELECT invalid_column FROM Students;
```
```
Semantic Error: Column 'invalid_column' does not exist in table 'Students' 
at line 1, column 8
```

### 3. Table Redeclaration Prevention

**Rule:** Cannot create a table that already exists.

**Example Error:**
```sql
CREATE TABLE Students (id INT);
CREATE TABLE Students (name TEXT);  -- Error!
```
```
Semantic Error: Table 'Students' already exists at line 2, column 1
```

### 4. INSERT Type Checking

**Rule:** Values in INSERT must match column types and count.

**Checks:**
- Number of values matches number of columns
- Each value type is compatible with column type

**Example Error:**
```sql
CREATE TABLE Students (id INT, name TEXT, age INT);
INSERT INTO Students VALUES (1, 'Alice');  -- Too few values
```
```
Semantic Error: Column count mismatch: table has 3 columns, 
but 2 values provided at line 2, column 1
```

**Type Mismatch:**
```sql
INSERT INTO Students VALUES ('text', 'Alice', 20);  -- 'text' not INT
```
```
Semantic Error: Type mismatch for column 'id': expected INT, got TEXT 
at line 1, column 1
```

### 5. WHERE Clause Type Checking

**Rule:** Comparisons must be between compatible types.

**Example Error:**
```sql
SELECT * FROM Students WHERE age = 'text';  -- INT compared to TEXT
```
```
Semantic Error: Type mismatch in comparison: column 'age' is INT, 
but compared with TEXT at line 1, column 35
```

### 6. Data Type Validation

**Rule:** Only INT, FLOAT, and TEXT are valid types.

**Example Error:**
```sql
CREATE TABLE Test (id VARCHAR);  -- Invalid type
```
```
Semantic Error: Invalid data type 'VARCHAR' for column 'id' at line 1, column 20
```

## 🎯 Type System

### Supported Types

| Type | Description | Compatible With | Examples |
|------|-------------|-----------------|----------|
| `INT` | Integer numbers | INT, FLOAT | 42, -10, 0 |
| `FLOAT` | Floating-point | INT, FLOAT | 3.14, 2.0 |
| `TEXT` | String values | TEXT only | 'Alice', 'Hello' |

### Type Compatibility Rules

1. **INT ↔ FLOAT:** Compatible
   - INT can be compared with FLOAT
   - FLOAT can be compared with INT

2. **TEXT ↔ TEXT:** Compatible
   - TEXT can only be compared with TEXT

3. **TEXT ↔ INT/FLOAT:** Incompatible
   - Cannot compare TEXT with numbers

### Type Inference

The analyzer automatically infers types from literals:
- Has decimal point → FLOAT
- All digits → INT
- Quoted string → TEXT

```python
_infer_type('42')     # → INT
_infer_type('3.14')   # → FLOAT
_infer_type('Alice')  # → TEXT
```

## 🌳 Annotated Parse Tree

The semantic analyzer creates an annotated parse tree with:
- **data_type** - Data type of expressions
- **symbol_ref** - Reference to symbol table entry

### Example Annotation

**Input:**
```sql
SELECT name FROM Students WHERE age > 20;
```

**Annotated Tree:**
```
SELECT
├── SELECT_LIST
│   └── IDENTIFIER (name) [type: TEXT, ref: Students.name]
├── KEYWORD (FROM)
├── IDENTIFIER (Students) [ref: TABLE:Students]
└── WHERE_CLAUSE
    └── COMPARISON
        ├── IDENTIFIER (age) [type: INT, ref: Students.age]
        ├── OPERATOR (>)
        └── LITERAL (20) [type: INT]
```

## 📝 Example

### Complete Example

**Input:**
```sql
CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT,
    gpa FLOAT
);

CREATE TABLE Courses (
    course_id INT,
    course_name TEXT
);

INSERT INTO Students VALUES (1, 'Alice', 20, 3.8);
INSERT INTO Students VALUES (2, 'Bob', 21, 3.5);

SELECT * FROM Students;
SELECT name, age FROM Students WHERE age > 20;

UPDATE Students SET age = 22 WHERE id = 1;
DELETE FROM Students WHERE age < 20;
```

**Symbol Table Output:**
```
SYMBOL TABLE:
------------------------------------------------------------

Table: Students
--------------------------------------------------
  id                   INT
  name                 TEXT
  age                  INT
  gpa                  FLOAT

Table: Courses
--------------------------------------------------
  course_id            INT
  course_name          TEXT
```

**Success Message:**
```
✅ Semantic Analysis Successful. Query is valid.
```

### Example with Errors

**Input:**
```sql
CREATE TABLE Students (id INT, name TEXT);
INSERT INTO Students VALUES (1);              -- Error: Column count mismatch
SELECT * FROM Courses;                         -- Error: Table doesn't exist
SELECT invalid_col FROM Students;              -- Error: Column doesn't exist
INSERT INTO Students VALUES ('text', 'Alice'); -- Error: Type mismatch
```

**Error Output:**
```
SEMANTIC ERRORS:
============================================================

Semantic Error: Column count mismatch: table has 2 columns, 
but 1 values provided at line 2, column 1

Semantic Error: Table 'Courses' does not exist at line 3, column 15

Semantic Error: Column 'invalid_col' does not exist in table 'Students' 
at line 4, column 8

Semantic Error: Type mismatch for column 'id': expected INT, got TEXT 
at line 5, column 1
```

## 🚨 Error Handling

### Error Structure

```python
{
    'type': 'SEMANTIC_ERROR',
    'message': 'Detailed error description',
    'line': line_number,
    'column': column_number
}
```

### Error Categories

1. **Identifier Errors:**
   - Table does not exist
   - Column does not exist
   - Table already exists (redeclaration)

2. **Type Errors:**
   - Type mismatch in INSERT
   - Type mismatch in WHERE comparison
   - Invalid data type in CREATE TABLE

3. **Count Errors:**
   - Column count mismatch in INSERT

## 🧪 Testing

### Test Cases

1. **Valid Program:**
   ```sql
   CREATE TABLE Test (id INT, name TEXT);
   INSERT INTO Test VALUES (1, 'Alice');
   SELECT * FROM Test;
   ```
   **Expected:** No errors

2. **Table Not Found:**
   ```sql
   SELECT * FROM NonExistent;
   ```
   **Expected:** "Table 'NonExistent' does not exist"

3. **Column Not Found:**
   ```sql
   CREATE TABLE Test (id INT);
   SELECT name FROM Test;
   ```
   **Expected:** "Column 'name' does not exist in table 'Test'"

4. **Type Mismatch:**
   ```sql
   CREATE TABLE Test (id INT);
   INSERT INTO Test VALUES ('text');
   ```
   **Expected:** "Type mismatch for column 'id': expected INT, got TEXT"

5. **Table Redeclaration:**
   ```sql
   CREATE TABLE Test (id INT);
   CREATE TABLE Test (name TEXT);
   ```
   **Expected:** "Table 'Test' already exists"

### Running Tests

```python
from lexer import LexicalAnalyzer
from parser import SyntaxAnalyzer
from semantic import SemanticAnalyzer

source = """
CREATE TABLE Test (id INT, name TEXT);
INSERT INTO Test VALUES (1, 'Alice');
SELECT * FROM Test;
"""

# Phase 01
lexer = LexicalAnalyzer(source)
lexer.tokenize()
tokens = lexer.get_tokens()

# Phase 02
parser = SyntaxAnalyzer(tokens)
parse_tree = parser.parse()

# Phase 03
semantic = SemanticAnalyzer(parse_tree)
success = semantic.analyze()

print(f"Success: {success}")
print(f"Errors: {len(semantic.get_errors())}")
print(f"Symbol Table:\n{semantic.get_symbol_table().dump()}")
```

## 📈 Performance

- **Time Complexity:** O(n) where n is number of nodes in parse tree
- **Space Complexity:** O(t + c) where t is number of tables and c is total columns

## 📊 Output Format

### Success Output

```
PHASE 03: SEMANTIC ANALYSIS
============================================================

✅ Semantic Analysis Successful. Query is valid.

SYMBOL TABLE:
------------------------------------------------------------

Table: Students
--------------------------------------------------
  id                   INT
  name                 TEXT
  age                  INT
  gpa                  FLOAT

ANNOTATED PARSE TREE (with semantic information):
------------------------------------------------------------
PROGRAM
  STATEMENT
    CREATE_TABLE [SUCCESS: ✓ Table 'Students' created with 4 columns]
      IDENTIFIER (Students) [ref: TABLE:Students]
      ...
```

### Error Output

```
PHASE 03: SEMANTIC ANALYSIS
============================================================

❌ Semantic Analysis Failed. 3 error(s) found.

SEMANTIC ERRORS:
============================================================

  SEMANTIC_ERROR: Table 'NonExistent' does not exist at line 5, position 15
  SEMANTIC_ERROR: Column 'invalid' does not exist in table 'Students' at line 7, position 8
  SEMANTIC_ERROR: Type mismatch for column 'age': expected INT, got TEXT at line 9, position 1
```

## 🔗 Integration

### Complete Pipeline

```python
from lexer import LexicalAnalyzer
from parser import SyntaxAnalyzer
from semantic import SemanticAnalyzer

def compile_sql(source_code):
    """Complete 3-phase compilation"""

    # Phase 01: Lexical Analysis
    lexer = LexicalAnalyzer(source_code)
    lexer.tokenize()
    tokens = lexer.get_tokens()

    if lexer.get_errors():
        return False, "Lexical errors found"

    # Phase 02: Syntax Analysis
    parser = SyntaxAnalyzer(tokens)
    parse_tree = parser.parse()

    if parser.get_errors():
        return False, "Syntax errors found"

    # Phase 03: Semantic Analysis
    semantic = SemanticAnalyzer(parse_tree)
    success = semantic.analyze()

    if not success:
        return False, semantic.get_errors()

    return True, semantic.get_symbol_table()
```

## 🎨 Graphical Output

The GUI provides graphical visualization of the annotated parse tree with:
- Color-coded nodes
- Type annotations visible
- Symbol references displayed
- Zoom and scroll capabilities

Access via:
- "Semantic Analysis" tab
- "🌳 Visualize Annotated Tree" button
- Keyboard shortcut: `Ctrl+A`

---

**Phase 03 Complete! ✅**

**All three phases implemented successfully! The compiler is now fully functional.** 🎉
