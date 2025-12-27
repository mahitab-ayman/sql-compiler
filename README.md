# SQL-like Compiler - CSCI415 Project

A complete compiler implementation for a SQL-like query language, built in three phases:
- **Phase 01**: Lexical Analyzer
- **Phase 02**: Syntax Analyzer
- **Phase 03**: Semantic Analyzer

## Project Structure

```
sql-compiler/
├── lexer.py              # Phase 01: Lexical Analyzer
├── parser.py             # Phase 02: Syntax Analyzer
├── semantic_analyzer.py  # Phase 03: Semantic Analyzer
├── visualizer.py         # Parse tree visualization
├── main.py               # Main driver program
├── sample_input.sql      # Sample valid queries
├── sample_input_errors.sql  # Sample queries with errors
└── README.md             # This file
```

## Features

### Phase 01: Lexical Analyzer
- Token classification (Keywords, Identifiers, Literals, Operators, Delimiters)
- Case-sensitive keyword recognition
- String literal handling with single quotes
- Numeric literal recognition (INT, FLOAT)
- Comment support:
  - Single-line comments: `--`
  - Multi-line comments: `## ... ##`
- Comprehensive error handling with line and column numbers

### Phase 02: Syntax Analyzer
- Recursive Descent Parsing
- Complete grammar support for:
  - CREATE TABLE
  - INSERT INTO
  - SELECT
  - UPDATE
  - DELETE
- Complex WHERE clause support (AND, OR, NOT, parentheses)
- Parse tree generation
- Error recovery mechanism

### Phase 03: Semantic Analyzer
- Symbol Table management
- Table and column existence verification
- Type checking (INT, FLOAT, TEXT)
- Type compatibility validation
- Redeclaration prevention
- Comprehensive error reporting

## Requirements

- Python 3.6 or higher
- Optional: `graphviz` for visual parse tree generation
  ```bash
  pip install graphviz
  ```
  Note: You also need to install Graphviz system package:
  - Windows: Download from https://graphviz.org/download/
  - Linux: `sudo apt-get install graphviz`
  - macOS: `brew install graphviz`

## Usage

### Basic Usage

```bash
python main.py sample_input.sql
```

### With Visual Parse Tree

```bash
python main.py sample_input.sql --visual
```

This will generate a PNG image of the parse tree (requires graphviz).

### Output

The compiler produces output for all three phases:

1. **Lexical Analysis**: List of tokens and any lexical errors
2. **Syntax Analysis**: Parse tree structure and any syntax errors
3. **Semantic Analysis**: 
   - Symbol table dump
   - Annotated parse tree with type information
   - Semantic error reports

## Supported SQL Syntax

### CREATE TABLE
```sql
CREATE TABLE table_name (
    column1 INT,
    column2 TEXT,
    column3 FLOAT
);
```

### INSERT INTO
```sql
INSERT INTO table_name VALUES (1, 'text', 3.14);
INSERT INTO table_name (col1, col2) VALUES (1, 'text');
```

### SELECT
```sql
SELECT * FROM table_name;
SELECT col1, col2 FROM table_name WHERE col1 > 10;
SELECT * FROM table_name WHERE col1 = 1 AND col2 < 5;
SELECT * FROM table_name WHERE NOT (col1 = 1 OR col2 = 2);
```

### UPDATE
```sql
UPDATE table_name SET col1 = 10 WHERE col2 = 'value';
UPDATE table_name SET col1 = 20, col2 = 'new' WHERE col3 > 5;
```

### DELETE
```sql
DELETE FROM table_name WHERE col1 = 1;
DELETE FROM table_name WHERE col1 > 10 OR col2 < 5;
```

## Error Handling

The compiler provides detailed error messages for:

### Lexical Errors
- Invalid characters
- Unclosed string literals
- Unclosed comments
- Invalid number formats

### Syntax Errors
- Missing keywords
- Unexpected tokens
- Missing delimiters
- Malformed statements

### Semantic Errors
- Table/column existence
- Type mismatches
- Redeclaration errors
- Type incompatibility in comparisons

## Example Output

```
================================================================
SQL-LIKE COMPILER - PHASE 01, 02, 03
================================================================

Input file: sample_input.sql

================================================================
PHASE 01: LEXICAL ANALYSIS
================================================================
TOKENS:
  <KEYWORD, 'CREATE', 1, 1>
  <KEYWORD, 'TABLE', 1, 8>
  <IDENTIFIER, 'Students', 1, 14>
  ...
Total tokens: 45

================================================================
PHASE 02: SYNTAX ANALYSIS
================================================================
PARSE TREE:
PROGRAM
  CREATE_TABLE
    KEYWORD (CREATE)
    KEYWORD (TABLE)
    IDENTIFIER (Students)
    ...

================================================================
PHASE 03: SEMANTIC ANALYSIS
================================================================
✓ Semantic Analysis Successful. Query is valid.

================================================================
SYMBOL TABLE
================================================================
Table: Students
  Columns:
    - id: INT
    - name: TEXT
    - age: INT
    - gpa: FLOAT
...
```

## Implementation Details

### Lexical Analyzer
- Character-by-character scanning
- State machine for token recognition
- Line and column tracking
- Error recovery and reporting

### Syntax Analyzer
- Recursive descent parsing
- Predictive parsing for grammar rules
- Panic-mode error recovery
- Parse tree construction

### Semantic Analyzer
- Hierarchical symbol table
- Type inference and checking
- Scope management
- Parse tree annotation

## Testing

Test files are provided:
- `sample_input.sql`: Valid queries covering all features
- `sample_input_errors.sql`: Queries with various error types

Run tests:
```bash
python main.py sample_input.sql
python main.py sample_input_errors.sql
```

## Notes

- All code is implemented from scratch (no external parsing libraries)
- Case-sensitive keyword matching
- Comprehensive error reporting with line/column numbers
- Visual parse tree generation (optional, requires graphviz)

## Authors

CSCI415 Compiler Design Project - Fall 2025

## License

Educational project for CSCI415 course.

