"""
Main driver for SQL-like Compiler
Integrates Lexical Analyzer, Syntax Analyzer, and Semantic Analyzer
"""

import sys
import os
from lexer import LexicalAnalyzer
from parser import SyntaxAnalyzer
from semantic_analyzer import SemanticAnalyzer
from visualizer import ParseTreeVisualizer


def read_file(filename):
    """Read source code from file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [--visual]")
        print("  --visual: Generate visual parse tree (requires graphviz)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    generate_visual = '--visual' in sys.argv
    
    # Read source code
    source_code = read_file(input_file)
    
    print("\n" + "=" * 60)
    print("SQL-LIKE COMPILER - PHASE 01, 02, 03")
    print("=" * 60)
    print(f"\nInput file: {input_file}\n")
    
    # Phase 01: Lexical Analysis
    print("\n" + "=" * 60)
    print("PHASE 01: LEXICAL ANALYSIS")
    print("=" * 60)
    lexer = LexicalAnalyzer(source_code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
    
    if lexer.get_errors():
        print("\nLexical analysis failed. Cannot proceed to syntax analysis.")
        return
    
    # Phase 02: Syntax Analysis
    print("\n" + "=" * 60)
    print("PHASE 02: SYNTAX ANALYSIS")
    print("=" * 60)
    parser = SyntaxAnalyzer(tokens)
    parse_tree = parser.parse()
    parser.print_parse_tree()
    
    if parser.get_errors():
        print("\nSyntax analysis failed. Cannot proceed to semantic analysis.")
        return
    
    # Phase 03: Semantic Analysis
    print("\n" + "=" * 60)
    print("PHASE 03: SEMANTIC ANALYSIS")
    print("=" * 60)
    semantic_analyzer = SemanticAnalyzer(parse_tree)
    success = semantic_analyzer.analyze()
    semantic_analyzer.print_results()
    
    # Generate visual parse tree if requested
    if generate_visual and parse_tree:
        print("\n" + "=" * 60)
        print("GENERATING VISUAL PARSE TREE")
        print("=" * 60)
        visualizer = ParseTreeVisualizer()
        output_file = os.path.splitext(input_file)[0] + "_parse_tree"
        try:
            visualizer.visualize(parse_tree, output_file)
            print(f"\nVisual parse tree saved to: {output_file}.png")
        except Exception as e:
            print(f"\nWarning: Could not generate visual parse tree: {e}")
            print("Falling back to ASCII visualization...")
            visualizer.print_ascii_tree(parse_tree)
    elif parse_tree and not generate_visual:
        # Always show ASCII tree in summary
        print("\n" + "=" * 60)
        print("PARSE TREE VISUALIZATION (ASCII)")
        print("=" * 60)
        visualizer = ParseTreeVisualizer()
        visualizer.print_ascii_tree(parse_tree)
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPILATION SUMMARY")
    print("=" * 60)
    lexical_errors = len(lexer.get_errors())
    syntax_errors = len(parser.get_errors())
    semantic_errors = len(semantic_analyzer.get_errors())
    
    print(f"Lexical Errors:   {lexical_errors}")
    print(f"Syntax Errors:    {syntax_errors}")
    print(f"Semantic Errors:  {semantic_errors}")
    
    if lexical_errors == 0 and syntax_errors == 0 and semantic_errors == 0:
        print("\n✓ Compilation successful! Query is valid.")
    else:
        print("\n✗ Compilation failed. Please fix the errors above.")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

