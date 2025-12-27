# Quick Start Guide

## Installation

1. **Clone or download the project**
   ```bash
   cd sql-compiler
   ```

2. **Install optional dependencies (for visual parse trees)**
   ```bash
   pip install graphviz
   ```
   Note: You also need Graphviz system package installed.

## Running the Compiler

### Basic Usage

```bash
python main.py sample_input.sql
```

This will run all three phases:
- Phase 01: Lexical Analysis
- Phase 02: Syntax Analysis  
- Phase 03: Semantic Analysis

### With Visual Parse Tree

```bash
python main.py sample_input.sql --visual
```

This generates a PNG image of the parse tree (requires graphviz).

### Testing Error Handling

```bash
python main.py sample_input_errors.sql
```

This file contains various errors to test error detection.

## Running Tests

```bash
python test_compiler.py
```

This runs a test suite with multiple test cases.

## Example Queries

### Create Table
```sql
CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT
);
```

### Insert Data
```sql
INSERT INTO Students VALUES (1, 'Alice', 20);
```

### Select Data
```sql
SELECT * FROM Students WHERE age > 18;
```

### Update Data
```sql
UPDATE Students SET age = 21 WHERE id = 1;
```

### Delete Data
```sql
DELETE FROM Students WHERE age < 18;
```

## Understanding Output

The compiler produces output in three sections:

1. **Lexical Analysis**: Shows all tokens found
2. **Syntax Analysis**: Shows the parse tree structure
3. **Semantic Analysis**: 
   - Symbol table dump
   - Annotated parse tree
   - Error reports (if any)

## Common Issues

### "graphviz not found"
- Install: `pip install graphviz`
- Also install system package: https://graphviz.org/download/

### "File not found"
- Make sure you're in the `sql-compiler` directory
- Check that the input file exists

### Import errors
- Make sure all Python files are in the same directory
- Check Python version: `python --version` (needs 3.6+)

## Next Steps

1. Read `README.md` for detailed documentation
2. Try modifying `sample_input.sql` with your own queries
3. Check `GITHUB_SETUP.md` to push to GitHub

