"""
Test script for SQL-like Compiler
Tests all three phases with various inputs
"""

import sys
from lexer import LexicalAnalyzer
from parser import SyntaxAnalyzer
from semantic_analyzer import SemanticAnalyzer


def test_lexical_analysis(source_code):
    """Test Phase 01: Lexical Analysis"""
    print("\n" + "=" * 60)
    print("TESTING PHASE 01: LEXICAL ANALYSIS")
    print("=" * 60)
    
    lexer = LexicalAnalyzer(source_code)
    tokens = lexer.tokenize()
    errors = lexer.get_errors()
    
    print(f"Tokens generated: {len(tokens)}")
    print(f"Errors found: {len(errors)}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error['message']}")
    
    return len(errors) == 0, tokens


def test_syntax_analysis(tokens):
    """Test Phase 02: Syntax Analysis"""
    print("\n" + "=" * 60)
    print("TESTING PHASE 02: SYNTAX ANALYSIS")
    print("=" * 60)
    
    parser = SyntaxAnalyzer(tokens)
    parse_tree = parser.parse()
    errors = parser.get_errors()
    
    print(f"Parse tree generated: {parse_tree is not None}")
    print(f"Errors found: {len(errors)}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error['message']} at line {error['line']}, column {error['column']}")
    
    return len(errors) == 0, parse_tree


def test_semantic_analysis(parse_tree):
    """Test Phase 03: Semantic Analysis"""
    print("\n" + "=" * 60)
    print("TESTING PHASE 03: SEMANTIC ANALYSIS")
    print("=" * 60)
    
    semantic_analyzer = SemanticAnalyzer(parse_tree)
    success = semantic_analyzer.analyze()
    errors = semantic_analyzer.get_errors()
    
    print(f"Semantic analysis passed: {success}")
    print(f"Errors found: {len(errors)}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error['message']} at line {error['line']}, column {error['column']}")
    else:
        print("\nSymbol Table:")
        print(semantic_analyzer.get_symbol_table().dump())
    
    return success


def run_test(test_name, source_code):
    """Run a complete test"""
    print("\n" + "=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)
    print(f"Source code:\n{source_code}")
    
    # Phase 01
    lex_success, tokens = test_lexical_analysis(source_code)
    if not lex_success:
        print("\n✗ Test failed at lexical analysis phase")
        return False
    
    # Phase 02
    syntax_success, parse_tree = test_syntax_analysis(tokens)
    if not syntax_success:
        print("\n✗ Test failed at syntax analysis phase")
        return False
    
    # Phase 03
    semantic_success = test_semantic_analysis(parse_tree)
    if not semantic_success:
        print("\n✗ Test failed at semantic analysis phase")
        return False
    
    print("\n✓ All phases passed!")
    return True


def main():
    """Main test function"""
    print("=" * 60)
    print("SQL-LIKE COMPILER - TEST SUITE")
    print("=" * 60)
    
    # Test 1: Simple CREATE TABLE
    test1 = """
CREATE TABLE Test (
    id INT,
    name TEXT
);
"""
    
    # Test 2: INSERT with VALUES
    test2 = """
CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT
);
INSERT INTO Students VALUES (1, 'Alice', 20);
"""
    
    # Test 3: SELECT with WHERE
    test3 = """
CREATE TABLE Products (
    id INT,
    price FLOAT,
    name TEXT
);
SELECT * FROM Products WHERE price > 10.5;
"""
    
    # Test 4: Complex WHERE clause
    test4 = """
CREATE TABLE Employees (
    id INT,
    salary FLOAT,
    department TEXT
);
SELECT id, salary FROM Employees WHERE salary > 50000 AND department = 'IT';
"""
    
    tests = [
        ("Simple CREATE TABLE", test1),
        ("INSERT with VALUES", test2),
        ("SELECT with WHERE", test3),
        ("Complex WHERE clause", test4)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_code in tests:
        try:
            if run_test(test_name, test_code):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test '{test_name}' raised exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()

