"""
GUI Application for SQL-like Compiler
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
from compiler.lexer import LexicalAnalyzer
from compiler.parser import SyntaxAnalyzer
from compiler.semantic_analyzer import SemanticAnalyzer
from gui.visualizer import ParseTreeVisualizer
from gui.tree_visualizer import TreeVisualizerWindow


class CompilerGUI:
    """Main GUI application for the SQL compiler"""

    def __init__(self, root):
        self.root = root
        self.root.title("SQL-like Compiler - Phase 01, 02, 03")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Current file path and parse tree
        self.current_file = None
        self.current_parse_tree = None
        self.current_annotated_tree = None

        # Create UI
        self.create_menu()
        self.create_widgets()

        # Load sample on startup
        self.load_sample()

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        edit_menu.add_command(label="Load Sample", command=self.load_sample)

        # Compile menu
        compile_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Compile", menu=compile_menu)
        compile_menu.add_command(label="Run All Phases", command=self.run_compiler, accelerator="F5")
        compile_menu.add_command(label="Phase 01: Lexical Analysis", command=self.run_lexical)
        compile_menu.add_command(label="Phase 02: Syntax Analysis", command=self.run_syntax)
        compile_menu.add_command(label="Phase 03: Semantic Analysis", command=self.run_semantic)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Visualize Parse Tree", command=self.visualize_parse_tree, accelerator="Ctrl+T")
        view_menu.add_command(label="Visualize Annotated Tree", command=self.visualize_annotated_tree, accelerator="Ctrl+A")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as_file())
        self.root.bind('<F5>', lambda e: self.run_compiler())
        self.root.bind('<Control-t>', lambda e: self.visualize_parse_tree())
        self.root.bind('<Control-a>', lambda e: self.visualize_annotated_tree())

    def create_widgets(self):
        """Create main widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left panel - Input
        left_frame = ttk.LabelFrame(main_frame, text="SQL Input", padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # Input text area
        self.input_text = scrolledtext.ScrolledText(
            left_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10),
            width=50,
            height=25
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # Input buttons
        input_btn_frame = ttk.Frame(left_frame)
        input_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(input_btn_frame, text="Clear", command=self.clear_input).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_btn_frame, text="Load File", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_btn_frame, text="Save File", command=self.save_file).pack(side=tk.LEFT)

        # Right panel - Output (Notebook with tabs)
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Tokens (Lexical Analysis)
        self.tokens_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.tokens_frame, text="Tokens")
        self.tokens_text = scrolledtext.ScrolledText(
            self.tokens_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.tokens_text.pack(fill=tk.BOTH, expand=True)

        # Tab 2: Parse Tree
        self.tree_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.tree_frame, text="Parse Tree")

        # Add button to visualize tree
        tree_btn_frame = ttk.Frame(self.tree_frame)
        tree_btn_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(tree_btn_frame, text="🌳 Visualize Parse Tree", 
                  command=self.visualize_parse_tree).pack(side=tk.LEFT)

        self.tree_text = scrolledtext.ScrolledText(
            self.tree_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.tree_text.pack(fill=tk.BOTH, expand=True)

        # Tab 3: Symbol Table & Annotated Tree
        self.symbol_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.symbol_frame, text="Semantic Analysis")

        # Add button to visualize annotated tree
        semantic_btn_frame = ttk.Frame(self.symbol_frame)
        semantic_btn_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(semantic_btn_frame, text="🌳 Visualize Annotated Tree", 
                  command=self.visualize_annotated_tree).pack(side=tk.LEFT)

        self.symbol_text = scrolledtext.ScrolledText(
            self.symbol_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.symbol_text.pack(fill=tk.BOTH, expand=True)

        # Tab 4: Errors
        self.errors_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.errors_frame, text="Errors")
        self.errors_text = scrolledtext.ScrolledText(
            self.errors_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED,
            foreground="red"
        )
        self.errors_text.pack(fill=tk.BOTH, expand=True)

        # Tab 5: Summary
        self.summary_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(self.summary_frame, text="Summary")
        self.summary_text = scrolledtext.ScrolledText(
            self.summary_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Bottom panel - Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Button(control_frame, text="▶ Run Compiler (F5)", 
                  command=self.run_compiler).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Phase 01: Lexical", 
                  command=self.run_lexical).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Phase 02: Syntax", 
                  command=self.run_syntax).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Phase 03: Semantic", 
                  command=self.run_semantic).pack(side=tk.LEFT, padx=(0, 5))

        # Separator
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Visualize buttons
        ttk.Button(control_frame, text="🌳 Visualize Tree", 
                  command=self.visualize_parse_tree).pack(side=tk.LEFT, padx=(0, 5))

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(control_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def visualize_parse_tree(self):
        """Open graphical parse tree visualizer"""
        if not self.current_parse_tree:
            messagebox.showinfo("Info", "No parse tree available. Please run the compiler first.")
            return

        TreeVisualizerWindow(self.root, self.current_parse_tree, "Parse Tree Visualization")

    def visualize_annotated_tree(self):
        """Open graphical annotated tree visualizer"""
        if not self.current_annotated_tree:
            messagebox.showinfo("Info", "No annotated tree available. Please run semantic analysis first.")
            return

        TreeVisualizerWindow(self.root, self.current_annotated_tree, "Annotated Parse Tree with Semantic Info")

    def clear_input(self):
        """Clear input text area"""
        self.input_text.delete(1.0, tk.END)
        self.status_var.set("Input cleared")

    def clear_all(self):
        """Clear all text areas"""
        self.input_text.delete(1.0, tk.END)
        self.clear_output()
        self.current_parse_tree = None
        self.current_annotated_tree = None
        self.status_var.set("All cleared")

    def clear_output(self):
        """Clear all output text areas"""
        for text_widget in [self.tokens_text, self.tree_text, self.symbol_text, 
                           self.errors_text, self.summary_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)

    def new_file(self):
        """Create new file"""
        self.clear_all()
        self.current_file = None
        self.status_var.set("New file")

    def open_file(self):
        """Open SQL file"""
        file_path = filedialog.askopenfilename(
            title="Open SQL File",
            filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, content)
                self.current_file = file_path
                self.status_var.set(f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        """Save current file"""
        if self.current_file:
            try:
                content = self.input_text.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_var.set(f"Saved: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save file with new name"""
        file_path = filedialog.asksaveasfilename(
            title="Save SQL File",
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                content = self.input_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_file = file_path
                self.status_var.set(f"Saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def load_sample(self):
        """Load sample SQL code"""
        sample_code = """-- Sample SQL-like queries

CREATE TABLE Students (
    id INT,
    name TEXT,
    age INT,
    gpa FLOAT
);

CREATE TABLE Courses (
    course_id INT,
    course_name TEXT,
    credits INT
);

INSERT INTO Students VALUES (1, 'Alice', 20, 3.8);
INSERT INTO Students VALUES (2, 'Bob', 21, 3.5);

SELECT * FROM Students;
SELECT name, age FROM Students WHERE age > 20;

UPDATE Students SET age = 22 WHERE id = 1;
DELETE FROM Students WHERE age < 20;
"""
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, sample_code)
        self.status_var.set("Sample code loaded")

    def get_source_code(self):
        """Get source code from input text area"""
        return self.input_text.get(1.0, tk.END).strip()

    def append_text(self, text_widget, text, state=tk.NORMAL):
        """Append text to a text widget"""
        text_widget.config(state=state)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
        text_widget.see(tk.END)

    def set_text(self, text_widget, text):
        """Set text in a text widget"""
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, text)
        text_widget.config(state=tk.DISABLED)
        text_widget.see(1.0)

    def format_annotated_tree(self, node, indent=0):
        """Format annotated parse tree with semantic information"""
        if not node:
            return ""

        result = "  " * indent + node.node_type
        if node.value:
            result += f" ({node.value})"

        # Add semantic annotations
        annotations = []
        if hasattr(node, 'data_type') and node.data_type:
            annotations.append(f"type: {node.data_type}")
        if hasattr(node, 'symbol_ref') and node.symbol_ref:
            annotations.append(f"ref: {node.symbol_ref}")

        if annotations:
            result += f" [{', '.join(annotations)}]"

        result += "\n"

        if hasattr(node, 'children'):
            for child in node.children:
                result += self.format_annotated_tree(child, indent + 1)

        return result

    def run_lexical(self):
        """Run Phase 01: Lexical Analysis"""
        source_code = self.get_source_code()
        if not source_code:
            messagebox.showwarning("Warning", "Please enter SQL code first.")
            return

        self.clear_output()
        self.status_var.set("Running Lexical Analysis...")
        self.root.update()

        try:
            lexer = LexicalAnalyzer(source_code)
            lexer.tokenize()
            tokens = lexer.get_tokens()
            errors = lexer.get_errors()

            tokens_output = "PHASE 01: LEXICAL ANALYSIS\n"
            tokens_output += "=" * 60 + "\n\n"
            tokens_output += f"Total tokens: {len(tokens)}\n\n"
            tokens_output += "TOKENS:\n"
            for token in tokens:
                tokens_output += f"  {token}\n"

            self.set_text(self.tokens_text, tokens_output)

            if errors:
                errors_output = "LEXICAL ERRORS:\n"
                errors_output += "=" * 60 + "\n\n"
                for error in errors:
                    errors_output += f"  {error['type']}: {error['message']} at line {error['line']}, column {error['column']}\n"
                self.append_text(self.errors_text, errors_output)
            else:
                self.append_text(self.errors_text, "✅ No lexical errors found.\n")

            self.status_var.set(f"Lexical Analysis complete: {len(tokens)} tokens, {len(errors)} errors")
            self.notebook.select(0)

        except Exception as e:
            import traceback
            error_msg = f"Error during lexical analysis:\n{str(e)}\n\n{traceback.format_exc()}"
            self.append_text(self.errors_text, error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Lexical Analysis failed")

    def run_syntax(self):
        """Run Phase 02: Syntax Analysis"""
        source_code = self.get_source_code()
        if not source_code:
            messagebox.showwarning("Warning", "Please enter SQL code first.")
            return

        self.status_var.set("Running Syntax Analysis...")
        self.root.update()

        try:
            lexer = LexicalAnalyzer(source_code)
            lexer.tokenize()
            tokens = lexer.get_tokens()
            lexical_errors = lexer.get_errors()

            if lexical_errors:
                messagebox.showwarning("Warning", "Lexical errors found. Please fix them first.")
                return

            parser = SyntaxAnalyzer(tokens)
            parse_tree = parser.parse()
            syntax_errors = parser.get_errors()

            # Store parse tree
            self.current_parse_tree = parse_tree

            tree_output = "PHASE 02: SYNTAX ANALYSIS\n"
            tree_output += "=" * 60 + "\n\n"
            if parse_tree:
                tree_output += "PARSE TREE:\n"
                tree_output += parse_tree.to_string()

                tree_output += "\n\nASCII PARSE TREE VISUALIZATION:\n"
                tree_output += "=" * 60 + "\n\n"
                visualizer = ParseTreeVisualizer()
                import io
                import sys
                old_stdout = sys.stdout
                sys.stdout = buffer = io.StringIO()
                visualizer.print_ascii_tree(parse_tree)
                sys.stdout = old_stdout
                tree_output += buffer.getvalue()

                tree_output += "\n\n💡 Tip: Click '🌳 Visualize Parse Tree' button for graphical view!\n"
            else:
                tree_output += "No parse tree generated.\n"

            self.set_text(self.tree_text, tree_output)

            if syntax_errors:
                errors_output = "\nSYNTAX ERRORS:\n"
                errors_output += "=" * 60 + "\n\n"
                for error in syntax_errors:
                    errors_output += f"  {error['type']}: {error['message']} at line {error['line']}, column {error['column']}\n"
                self.append_text(self.errors_text, errors_output)
            else:
                self.append_text(self.errors_text, "✅ No syntax errors found.\n")

            self.status_var.set(f"Syntax Analysis complete: {len(syntax_errors)} errors")
            self.notebook.select(1)

        except Exception as e:
            import traceback
            error_msg = f"Error during syntax analysis:\n{str(e)}\n\n{traceback.format_exc()}"
            self.append_text(self.errors_text, error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Syntax Analysis failed")

    def run_semantic(self):
        """Run Phase 03: Semantic Analysis"""
        source_code = self.get_source_code()
        if not source_code:
            messagebox.showwarning("Warning", "Please enter SQL code first.")
            return

        self.status_var.set("Running Semantic Analysis...")
        self.root.update()

        try:
            lexer = LexicalAnalyzer(source_code)
            lexer.tokenize()
            tokens = lexer.get_tokens()
            lexical_errors = lexer.get_errors()

            if lexical_errors:
                messagebox.showwarning("Warning", "Lexical errors found. Please fix them first.")
                return

            parser = SyntaxAnalyzer(tokens)
            parse_tree = parser.parse()
            syntax_errors = parser.get_errors()

            if syntax_errors:
                messagebox.showwarning("Warning", "Syntax errors found. Please fix them first.")
                return

            if not parse_tree:
                messagebox.showwarning("Warning", "No parse tree generated.")
                return

            semantic_analyzer = SemanticAnalyzer(parse_tree)
            success = semantic_analyzer.analyze()
            semantic_errors = semantic_analyzer.get_errors()
            symbol_table = semantic_analyzer.get_symbol_table()
            annotated_tree = semantic_analyzer.annotated_tree

            # Store annotated tree
            self.current_annotated_tree = annotated_tree

            symbol_output = "PHASE 03: SEMANTIC ANALYSIS\n"
            symbol_output += "=" * 60 + "\n\n"

            symbol_output += semantic_analyzer.get_success_message() + "\n\n"

            symbol_output += "SYMBOL TABLE:\n"
            symbol_output += "-" * 60 + "\n"
            symbol_output += symbol_table.dump() + "\n\n"

            if annotated_tree:
                symbol_output += "\nANNOTATED PARSE TREE (with semantic information):\n"
                symbol_output += "-" * 60 + "\n"
                symbol_output += self.format_annotated_tree(annotated_tree)

                symbol_output += "\n\n💡 Tip: Click '🌳 Visualize Annotated Tree' button for graphical view!\n"

            self.set_text(self.symbol_text, symbol_output)

            if semantic_errors:
                errors_output = "\nSEMANTIC ERRORS:\n"
                errors_output += "=" * 60 + "\n\n"
                for error in semantic_errors:
                    errors_output += f"  {error['type']}: {error['message']} at line {error['line']}, position {error['column']}\n"
                self.append_text(self.errors_text, errors_output)
            else:
                self.append_text(self.errors_text, "✅ No semantic errors found.\n")

            self.status_var.set(f"Semantic Analysis complete: {len(semantic_errors)} errors")
            self.notebook.select(2)

        except Exception as e:
            import traceback
            error_msg = f"Error during semantic analysis:\n{str(e)}\n\n{traceback.format_exc()}"
            self.append_text(self.errors_text, error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Semantic Analysis failed")

    def run_compiler(self):
        """Run all three phases of the compiler"""
        source_code = self.get_source_code()
        if not source_code:
            messagebox.showwarning("Warning", "Please enter SQL code first.")
            return

        self.clear_output()
        self.status_var.set("Running all compiler phases...")
        self.root.update()

        try:
            # Phase 01
            self.status_var.set("Phase 01: Lexical Analysis...")
            self.root.update()
            lexer = LexicalAnalyzer(source_code)
            lexer.tokenize()
            tokens = lexer.get_tokens()
            lexical_errors = lexer.get_errors()

            tokens_output = "PHASE 01: LEXICAL ANALYSIS\n"
            tokens_output += "=" * 60 + "\n\n"
            tokens_output += f"Total tokens: {len(tokens)}\n\n"
            tokens_output += "TOKENS:\n"
            for token in tokens:
                tokens_output += f"  {token}\n"
            self.set_text(self.tokens_text, tokens_output)

            # Phase 02
            self.status_var.set("Phase 02: Syntax Analysis...")
            self.root.update()
            parser = SyntaxAnalyzer(tokens)
            parse_tree = parser.parse()
            syntax_errors = parser.get_errors()

            self.current_parse_tree = parse_tree

            tree_output = "PHASE 02: SYNTAX ANALYSIS\n"
            tree_output += "=" * 60 + "\n\n"
            if parse_tree:
                tree_output += "PARSE TREE:\n"
                tree_output += parse_tree.to_string()

                tree_output += "\n\nASCII PARSE TREE VISUALIZATION:\n"
                tree_output += "=" * 60 + "\n\n"
                visualizer = ParseTreeVisualizer()
                import io
                import sys
                old_stdout = sys.stdout
                sys.stdout = buffer = io.StringIO()
                visualizer.print_ascii_tree(parse_tree)
                sys.stdout = old_stdout
                tree_output += buffer.getvalue()

                tree_output += "\n\n💡 Tip: Click '🌳 Visualize Parse Tree' button for graphical view!\n"
            else:
                tree_output += "No parse tree generated.\n"
            self.set_text(self.tree_text, tree_output)

            # Phase 03
            self.status_var.set("Phase 03: Semantic Analysis...")
            self.root.update()
            semantic_analyzer = None
            semantic_errors = []
            symbol_table = None
            annotated_tree = None

            if parse_tree:
                semantic_analyzer = SemanticAnalyzer(parse_tree)
                success = semantic_analyzer.analyze()
                semantic_errors = semantic_analyzer.get_errors()
                symbol_table = semantic_analyzer.get_symbol_table()
                annotated_tree = semantic_analyzer.annotated_tree

                self.current_annotated_tree = annotated_tree

                symbol_output = "PHASE 03: SEMANTIC ANALYSIS\n"
                symbol_output += "=" * 60 + "\n\n"

                symbol_output += semantic_analyzer.get_success_message() + "\n\n"

                symbol_output += "SYMBOL TABLE:\n"
                symbol_output += "-" * 60 + "\n"
                symbol_output += symbol_table.dump() + "\n\n"

                if annotated_tree:
                    symbol_output += "\nANNOTATED PARSE TREE (with semantic information):\n"
                    symbol_output += "-" * 60 + "\n"
                    symbol_output += self.format_annotated_tree(annotated_tree)

                    symbol_output += "\n\n💡 Tip: Click '🌳 Visualize Annotated Tree' button for graphical view!\n"

                self.set_text(self.symbol_text, symbol_output)
            else:
                self.set_text(self.symbol_text, "No parse tree available for semantic analysis.\n")

            # Collect all errors
            all_errors = []
            if lexical_errors:
                all_errors.append("LEXICAL ERRORS:\n" + "=" * 60 + "\n")
                for error in lexical_errors:
                    all_errors.append(f"  {error['type']}: {error['message']} at line {error['line']}, column {error['column']}\n")

            if syntax_errors:
                all_errors.append("\nSYNTAX ERRORS:\n" + "=" * 60 + "\n")
                for error in syntax_errors:
                    all_errors.append(f"  {error['type']}: {error['message']} at line {error['line']}, column {error['column']}\n")

            if semantic_errors:
                all_errors.append("\nSEMANTIC ERRORS:\n" + "=" * 60 + "\n")
                for error in semantic_errors:
                    all_errors.append(f"  {error['type']}: {error['message']} at line {error['line']}, position {error['column']}\n")

            if all_errors:
                self.set_text(self.errors_text, "".join(all_errors))
            else:
                self.set_text(self.errors_text, "✅ No errors found in any phase.\n")

            # Summary
            summary_output = "COMPILATION SUMMARY\n"
            summary_output += "=" * 60 + "\n\n"
            summary_output += f"Lexical Errors:   {len(lexical_errors)}\n"
            summary_output += f"Syntax Errors:    {len(syntax_errors)}\n"
            summary_output += f"Semantic Errors:  {len(semantic_errors)}\n\n"

            if len(lexical_errors) == 0 and len(syntax_errors) == 0 and len(semantic_errors) == 0:
                summary_output += "✅ Compilation successful! Query is valid.\n"
            else:
                summary_output += "❌ Compilation failed. Please fix the errors above.\n"

            self.set_text(self.summary_text, summary_output)

            self.notebook.select(4)

            total_errors = len(lexical_errors) + len(syntax_errors) + len(semantic_errors)
            if total_errors == 0:
                self.status_var.set("✅ Compilation successful!")
            else:
                self.status_var.set(f"Compilation complete with {total_errors} error(s)")

        except Exception as e:
            import traceback
            error_msg = f"Error during compilation:\n{str(e)}\n\n{traceback.format_exc()}"
            self.append_text(self.errors_text, error_msg)
            messagebox.showerror("Error", error_msg)
            self.status_var.set("Compilation failed")

    def show_about(self):
        """Show about dialog"""
        about_text = """SQL-like Compiler
Version 2.0

A three-phase compiler implementation:
- Phase 01: Lexical Analysis
- Phase 02: Syntax Analysis  
- Phase 03: Semantic Analysis

Features:
- Tokenization of SQL-like statements
- Parse tree generation
- Symbol table management
- Type checking
- Annotated parse tree with semantic info
- 🌳 GRAPHICAL tree visualization
- Error reporting
- Visual parse tree output

Developed for educational purposes.
"""
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
