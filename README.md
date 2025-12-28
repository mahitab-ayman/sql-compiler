# SQL-like Compiler - Complete Implementation

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

A complete three-phase compiler for a simplified SQL-like query language, built from scratch without using external parsing libraries or tools.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Phases](#phases)
- [Screenshots](#screenshots)
- [Technical Details](#technical-details)
- [Requirements](#requirements)
- [Team](#team)

## 🎯 Overview

This project implements a full compiler pipeline for SQL-like queries, consisting of three phases:

1. **Phase 01: Lexical Analysis** - Tokenization of source code
2. **Phase 02: Syntax Analysis** - Parse tree generation using recursive descent parsing
3. **Phase 03: Semantic Analysis** - Type checking and symbol table management

The compiler includes a professional GUI with graphical parse tree visualization.

## ✨ Features

### Core Features
- ✅ Complete lexical analysis with error detection
- ✅ Syntax analysis with detailed parse tree generation
- ✅ Semantic analysis with type checking
- ✅ Symbol table management
- ✅ Comprehensive error reporting with line/column numbers
- ✅ Support for CREATE, INSERT, SELECT, UPDATE, DELETE statements

### GUI Features
- 🎨 Modern Tkinter-based graphical interface
- 🌳 **Graphical parse tree visualization** (color-coded, zoomable)
- 📊 Multiple output tabs (Tokens, Parse Tree, Semantic Analysis, Errors, Summary)
- 💾 File operations (New, Open, Save, Save As)
- ⌨️ Keyboard shortcuts (F5 to compile, Ctrl+T for tree visualization)
- 🔍 Zoom in/out for tree diagrams

### Advanced Features
- Annotated parse tree with semantic information
- ASCII and graphical tree representations
- Type compatibility checking (INT, FLOAT, TEXT)
- Column and table existence validation
- Type mismatch detection in INSERT and WHERE clauses

## 📁 Project Structure

```
sql-compiler/
├── README.md                      # This file
├── PHASE_01_README.md            # Lexical analysis documentation
├── PHASE_02_README.md            # Syntax analysis documentation
├── PHASE_03_README.md            # Semantic analysis documentation
│
├── lexer.py                      # Phase 01: Lexical Analyzer
├── parser.py                     # Phase 02: Syntax Analyzer
├── semantic.py                   # Phase 03: Semantic Analyzer
│
├── gui.py                        # Main GUI application
├── visualizer.py                 # ASCII tree visualizer
├── tree_visualizer.py            # Graphical tree visualizer
│
├── sample.sql                    # Sample SQL input file
└── requirements.txt              # Python dependencies (minimal)
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Tkinter (usually comes with Python)

### Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sql-compiler
   ```

2. **Verify Python installation:**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

3. **Run the GUI:**
   ```bash
   python gui.py
   ```

That's it! No external dependencies needed.

## 💻 Usage

### Using the GUI (Recommended)

1. **Launch the application:**
   ```bash
   python gui.py
   ```

2. **Write or load SQL code:**
   - Type SQL queries in the left panel
   - Or click "Load File" to open a `.sql` file
   - Or use the pre-loaded sample code

3. **Run the compiler:**
   - Click "▶ Run Compiler (F5)" or press `F5`
   - View results in the tabs:
     - **Tokens** - Lexical analysis output
     - **Parse Tree** - Syntax analysis output
     - **Semantic Analysis** - Symbol table and annotated tree
     - **Errors** - All compilation errors
     - **Summary** - Overall compilation status

4. **Visualize the parse tree:**
   - Click "🌳 Visualize Tree" button (or press `Ctrl+T`)
   - A popup window shows a graphical tree diagram
   - Use Zoom In/Out buttons or mouse wheel to zoom
   - Scroll to navigate large trees

5. **Visualize the annotated tree:**
   - Go to "Semantic Analysis" tab
   - Click "🌳 Visualize Annotated Tree" (or press `Ctrl+A`)
   - View semantic information (types, symbol references)

### Using Command Line

You can also run individual phases programmatically:

```python
from lexer import LexicalAnalyzer
from parser import SyntaxAnalyzer
from semantic import SemanticAnalyzer

# Source code
source = """
CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT
);

INSERT INTO Students VALUES (1, 'Alice', 20);
SELECT * FROM Students;
"""

# Phase 01: Lexical Analysis
lexer = LexicalAnalyzer(source)
lexer.tokenize()
tokens = lexer.get_tokens()
print(f"Tokens: {len(tokens)}")

# Phase 02: Syntax Analysis
parser = SyntaxAnalyzer(tokens)
parse_tree = parser.parse()
print("Parse tree generated")

# Phase 03: Semantic Analysis
semantic = SemanticAnalyzer(parse_tree)
success = semantic.analyze()
print(f"Semantic analysis: {'Success' if success else 'Failed'}")
print(f"Symbol table: {semantic.get_symbol_table()}")
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Run all compiler phases |
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save file |
| `Ctrl+T` | Visualize parse tree |
| `Ctrl+A` | Visualize annotated tree |

## 📚 Phases

### Phase 01: Lexical Analysis

**Purpose:** Break source code into tokens

**Features:**
- Recognizes keywords (CREATE, INSERT, SELECT, UPDATE, DELETE, etc.)
- Identifies operators (=, <, >, <=, >=, <>, *)
- Extracts literals (integers, floats, strings)
- Detects identifiers (table/column names)
- Handles delimiters (parentheses, commas, semicolons)
- Reports lexical errors (invalid characters, unclosed strings)

**Output:** List of tokens with type, lexeme, line, and column

[📖 Read Phase 01 Documentation](PHASE_01_README.md)

### Phase 02: Syntax Analysis

**Purpose:** Build parse tree from tokens

**Features:**
- Recursive descent parser
- Supports all SQL-like statements
- Generates detailed parse tree
- ASCII tree visualization
- Error recovery and synchronization
- Reports syntax errors with context

**Output:** Parse tree structure + ASCII visualization

[📖 Read Phase 02 Documentation](PHASE_02_README.md)

### Phase 03: Semantic Analysis

**Purpose:** Validate semantic correctness

**Features:**
- Symbol table management
- Table existence verification
- Column existence verification
- Type checking (INT, FLOAT, TEXT)
- Type compatibility in INSERT statements
- Type compatibility in WHERE clauses
- Redeclaration prevention
- Annotated parse tree with semantic information

**Output:** Symbol table + annotated parse tree + semantic errors

[📖 Read Phase 03 Documentation](PHASE_03_README.md)

## 🖼️ Screenshots

### Main Interface
The main GUI shows:
- SQL input panel (left)
- Multi-tab output panel (right)
- Control buttons and status bar (bottom)

### Graphical Parse Tree
- Color-coded nodes by statement type
- Zoom and scroll capabilities
- Lines connecting parent-child nodes
- Clear node labels with values

### Semantic Analysis
- Symbol table with all tables and columns
- Annotated parse tree with type information
- Success/failure messages

## 🔧 Technical Details

### Language Grammar

```
program         → statement+
statement       → sql_statement ';'
sql_statement   → create_table | insert | select | update | delete

create_table    → 'CREATE' 'TABLE' identifier '(' column_list ')'
column_list     → column_def (',' column_def)*
column_def      → identifier data_type
data_type       → 'INT' | 'FLOAT' | 'TEXT'

insert          → 'INSERT' 'INTO' identifier 'VALUES' value_list
value_list      → '(' expression (',' expression)* ')'

select          → 'SELECT' select_list 'FROM' identifier where_clause?
select_list     → '*' | identifier (',' identifier)*

update          → 'UPDATE' identifier 'SET' assignment_list where_clause?
assignment_list → assignment (',' assignment)*
assignment      → identifier '=' expression

delete          → 'DELETE' 'FROM' identifier where_clause?
where_clause    → 'WHERE' condition

condition       → simple_condition (('AND' | 'OR') simple_condition)*
simple_condition→ identifier comparison_op expression
comparison_op   → '=' | '<' | '>' | '<=' | '>=' | '<>' | '!='

expression      → identifier | literal
literal         → INT_LITERAL | FLOAT_LITERAL | STRING_LITERAL
identifier      → [a-zA-Z_][a-zA-Z0-9_]*
```

### Supported Data Types

| Type | Description | Example |
|------|-------------|---------|
| `INT` | Integer numbers | `42`, `-10`, `0` |
| `FLOAT` | Floating-point numbers | `3.14`, `-0.5`, `2.0` |
| `TEXT` | String values | `'Alice'`, `'Hello World'` |

### Supported SQL Statements

#### CREATE TABLE
```sql
CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT,
    gpa FLOAT
);
```

#### INSERT INTO
```sql
INSERT INTO Students VALUES (1, 'Alice', 20, 3.8);
```

#### SELECT
```sql
-- Select all columns
SELECT * FROM Students;

-- Select specific columns
SELECT name, age FROM Students;

-- Select with WHERE clause
SELECT name, age FROM Students WHERE age > 20;
```

#### UPDATE
```sql
UPDATE Students SET age = 22 WHERE id = 1;
```

#### DELETE
```sql
DELETE FROM Students WHERE age < 18;
```

### Error Types

#### Lexical Errors
- Invalid characters
- Unclosed string literals
- Malformed numbers

#### Syntax Errors
- Missing keywords (INTO, FROM, WHERE, etc.)
- Missing semicolons
- Unbalanced parentheses
- Invalid statement structure

#### Semantic Errors
- Table does not exist
- Column does not exist
- Type mismatch in INSERT
- Type mismatch in WHERE clause
- Table redeclaration
- Column count mismatch

## 📦 Requirements

### System Requirements
- **OS:** Windows, macOS, or Linux
- **Python:** 3.8 or higher
- **RAM:** 512 MB minimum
- **Disk:** 10 MB for source files

### Python Dependencies
- `tkinter` (built-in with Python)
- No external packages required!

## 👥 Team

**Project:** SQL-like Compiler  
**Course:** CSCI415 - Compiler Design  
**Semester:** Fall 2025  



---

**Happy Compiling! 🚀**

*Last updated: December 28, 2025*
