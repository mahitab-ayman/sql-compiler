"""
Semantic Analyzer for SQL Compiler
"""
class SymbolTable:
    """Manages tables and their column information"""
    def __init__(self):
        self.tables = {} # {table_name: {column_name: data_type}}
        self.type = "SymbolTable"

    def add_table(self, table_name, columns):
        if table_name in self.tables:
            return False
        self.tables[table_name] = columns
        return True

    def table_exists(self, table_name):
        return table_name in self.tables

    def get_table_columns(self, table_name):
        return self.tables.get(table_name, {})

    def get_all_columns(self, table_name):
        if table_name in self.tables:
            return list(self.tables[table_name].keys())
        return []

    def get_column_type(self, table_name, column_name):
        if table_name in self.tables:
            return self.tables[table_name].get(column_name)
        return None

    def get_tables(self):
        return list(self.tables.keys())

    def __str__(self):
        if not self.tables:
            return "(Empty)"
        result = []
        for table_name, columns in self.tables.items():
            result.append(f"\nTable: {table_name}")
            result.append("-" * 50)
            for col_name, col_type in columns.items():
                result.append(f"  {col_name:<20} {col_type}")
        return "\n".join(result)

    def dump(self):
        return str(self)

    def __repr__(self):
        return f"SymbolTable(tables={len(self.tables)})"


class SemanticAnalyzer:
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.annotated_tree = None
        self.success = False
        self.type = "SemanticAnalyzer"

    def analyze(self):
        if not self.parse_tree:
            self.add_error("No parse tree provided", 0, 0)
            self.success = False
            return False
        try:
            self.annotated_tree = self._analyze_node(self.parse_tree)
            self.success = len(self.errors) == 0
            return self.success
        except Exception as e:
            import traceback
            self.add_error(f"Semantic analysis failed: {str(e)}", 0, 0)
            print(f"DEBUG: Exception in semantic analysis: {traceback.format_exc()}")
            self.success = False
            return False

    def _create_parse_node(self, node_type, value=None, line=0, column=0):
        try:
            from parser import ParseTreeNode
            return ParseTreeNode(node_type, value, line=line, column=column)
        except:
            class ParseNode:
                def __init__(self, node_type, value=None, line=0, column=0):
                    self.node_type = node_type
                    self.value = value
                    self.line = line if line else 0
                    self.column = column if column else 0
                    self.children = []
                    self.data_type = None
                    self.symbol_ref = None
                def add_child(self, child):
                    if child:
                        self.children.append(child)
            return ParseNode(node_type, value, line, column)

    def _safe_get_line_column(self, node):
        """Safe line/column extraction"""
        return (getattr(node, 'line', 0), getattr(node, 'column', 0))

    def _analyze_node(self, node):
        if not node:
            return None
        annotated = self._create_parse_node(node.node_type, node.value,
                                           getattr(node, 'line', 0),
                                           getattr(node, 'column', 0))
        if hasattr(node, 'data_type'):
            annotated.data_type = node.data_type
        if hasattr(node, 'symbol_ref'):
            annotated.symbol_ref = node.symbol_ref

        if node.node_type == "PROGRAM":
            if hasattr(node, 'children'):
                for child in node.children:
                    annotated_child = self._analyze_node(child)
                    if annotated_child:
                        annotated.add_child(annotated_child)
        elif node.node_type == "STATEMENT":
            if hasattr(node, 'children'):
                for child in node.children:
                    annotated_child = self._analyze_node(child)
                    if annotated_child:
                        annotated.add_child(annotated_child)
        elif node.node_type == "CREATE_TABLE":
            self._analyze_create_table(node, annotated)
        elif node.node_type == "INSERT":
            self._analyze_insert(node, annotated)
        elif node.node_type == "SELECT":
            self._analyze_select(node, annotated)
        elif node.node_type == "UPDATE":
            self._analyze_update(node, annotated)
        elif node.node_type == "DELETE":
            self._analyze_delete(node, annotated)
        elif node.node_type == "IDENTIFIER":
            pass  # Handled by parent statement
        elif hasattr(node, 'children'):
            for child in node.children:
                annotated_child = self._analyze_node(child)
                if annotated_child:
                    annotated.add_child(annotated_child)
        return annotated

    def _resolve_column_ambiguity(self, column_name, table_list):
        """Resolve column ambiguity across multiple tables"""
        matches = []
        for table_name in table_list:
            col_type = self.symbol_table.get_column_type(table_name, column_name)
            if col_type:
                matches.append((table_name, col_type))

        line, col = 0, 0
        if hasattr(self, 'current_node_info') and self.current_node_info:
            line, col = self._safe_get_line_column(self.current_node_info)

        if len(matches) == 0:
            self.add_error(
                f"Column '{column_name}' does not exist in any of the selected tables: {', '.join(table_list)}",
                line, col
            )
            return None
        elif len(matches) > 1:
            tables = [t[0] for t in matches]
            self.add_error(
                f"Column '{column_name}' is ambiguous (exists in tables: {', '.join(tables)})",
                line, col
            )
            return None
        else:
            return matches[0]

    def _analyze_create_table(self, node, annotated):
        table_name = None
        columns = {}
        if not hasattr(node, 'children'):
            return
        for child in node.children:
            annotated_child = self._create_parse_node(child.node_type, child.value,
                                                     getattr(child, 'line', 0),
                                                     getattr(child, 'column', 0))
            if hasattr(child, 'data_type'):
                annotated_child.data_type = child.data_type
            if hasattr(child, 'symbol_ref'):
                annotated_child.symbol_ref = child.symbol_ref

            if child.node_type == "IDENTIFIER" and table_name is None:
                table_name = child.value
                annotated_child.symbol_ref = f"TABLE:{table_name}"
                annotated.add_child(annotated_child)
            elif child.node_type == "COLUMN_LIST":
                columns = self._extract_columns_from_list(child)
                annotated_child = self._analyze_node(child)
                annotated.add_child(annotated_child)
            else:
                annotated.add_child(annotated_child)

        if table_name and columns:
            line, col = self._safe_get_line_column(node)
            if self.symbol_table.table_exists(table_name):
                self.add_error(f"Table '{table_name}' already exists", line, col)
            else:
                self.symbol_table.add_table(table_name, columns)
                success_node = self._create_parse_node("SUCCESS",
                    f"✓ Table '{table_name}' created with {len(columns)} columns",
                    line, col)
                annotated.add_child(success_node)

    def _extract_columns_from_list(self, column_list_node):
        columns = {}
        if not hasattr(column_list_node, 'children'):
            return columns
        for child in column_list_node.children:
            if child.node_type == "COLUMN_DEFINITION":
                col_name = None
                col_type = None
                if hasattr(child, 'children'):
                    for col_child in child.children:
                        if col_child.node_type == "IDENTIFIER":
                            col_name = col_child.value
                        elif col_child.node_type == "DATA_TYPE":
                            col_type = col_child.value
                if col_name and col_type:
                    line, col = self._safe_get_line_column(child)
                    if col_type not in ['INT', 'FLOAT', 'TEXT']:
                        self.add_error(f"Invalid data type '{col_type}' for column '{col_name}'", line, col)
                    else:
                        columns[col_name] = col_type
        return columns

    def _analyze_insert(self, node, annotated):
        table_name = None
        values = []
        if not hasattr(node, 'children'):
            return
        
        # ✅ FIXED: Extract table name FIRST
        for child in node.children:
            if child.node_type == "IDENTIFIER" and table_name is None:
                table_name = child.value
        
        line, col = self._safe_get_line_column(node)
        
        # ✅ FIXED: Table existence check FIRST - STOP if table doesn't exist
        if table_name and not self.symbol_table.table_exists(table_name):
            self.add_error(f"Table '{table_name}' does not exist", line, col)
            # Add children anyway for tree visualization
            for child in node.children:
                annotated.add_child(self._analyze_node(child))
            return
        
        # Table exists - now safe to do detailed checks
        for child in node.children:
            annotated_child = self._analyze_node(child)
            annotated.add_child(annotated_child)
            if child.node_type == "IDENTIFIER" and table_name is None:
                table_name = child.value
            elif child.node_type == "VALUE_LIST":
                values = self._extract_values(child)
        
        if table_name:
            columns = self.symbol_table.get_table_columns(table_name)
            if len(values) != len(columns):
                self.add_error(
                    f"Column count mismatch: table has {len(columns)} columns, but {len(values)} values provided",
                    line, col
                )
                return
            
            col_names = list(columns.keys())
            has_errors = False
            for i, (value, value_type) in enumerate(values):
                col_name = col_names[i]
                expected_type = columns[col_name]
                if not self._types_compatible(expected_type, value_type):
                    self.add_error(
                        f"Type mismatch for column '{col_name}': expected {expected_type}, got {value_type}",
                        line, col
                    )
                    has_errors = True
            
            if not has_errors:
                success_node = self._create_parse_node("SUCCESS",
                    f"✓ INSERT values match table '{table_name}' schema",
                    line, col)
                annotated.add_child(success_node)

    def _extract_values(self, value_list_node):
        values = []
        if not hasattr(value_list_node, 'children'):
            return values
        for child in value_list_node.children:
            if child.node_type == "LITERAL":
                value = child.value
                value_type = child.data_type if hasattr(child, 'data_type') and child.data_type else self._infer_type(value)
                values.append((value, value_type))
        return values

    def _analyze_select(self, node, annotated):
        table_names = []
        if not hasattr(node, 'children'):
            return
        
        # ✅ FIXED: Extract ALL table names FIRST
        for child in node.children:
            if child.node_type == "TABLE_LIST":
                table_names = self._extract_table_names(child)
                break
        
        line, col = self._safe_get_line_column(node)
        
        # ✅ FIXED: Check ALL tables exist FIRST
        for table_name in table_names:
            if not self.symbol_table.table_exists(table_name):
                self.add_error(f"Table '{table_name}' does not exist", line, col)
        
        # Only continue if ALL tables exist
        all_tables_exist = all(self.symbol_table.table_exists(t) for t in table_names)
        if not all_tables_exist:
            # Still build tree for visualization
            for child in node.children:
                annotated.add_child(self._analyze_node(child))
            return
        
        # All tables exist - safe to analyze columns/WHERE
        for child in node.children:
            annotated_child = self._analyze_node(child)
            annotated.add_child(annotated_child)
        
        columns = self._extract_select_columns(node)
        has_errors = False
        if table_names and columns and '*' not in columns:
            for col in columns:
                resolved = self._resolve_column_ambiguity(col, table_names)
                if not resolved:
                    has_errors = True
        
        # Analyze WHERE (safe now)
        for child in node.children:
            if child.node_type == "WHERE_CLAUSE":
                self._analyze_where_clause(child, table_names)
        
        if table_names and not has_errors:
            success_node = self._create_parse_node("SUCCESS",
                f"✓ SELECT from tables {', '.join(table_names)} is valid",
                line, col)
            annotated.add_child(success_node)

    def _extract_table_names(self, table_list_node):
        tables = []
        if not hasattr(table_list_node, 'children'):
            return tables
        for child in table_list_node.children:
            if child.node_type == "IDENTIFIER":
                tables.append(child.value)
        return tables

    def _extract_select_columns(self, select_node):
        columns = []
        if not hasattr(select_node, 'children'):
            return columns
        for child in select_node.children:
            if child.node_type == "SELECT_LIST":
                if hasattr(child, 'children'):
                    for id_child in child.children:
                        if id_child.node_type == "IDENTIFIER_LIST":
                            for idd in id_child.children:
                                if idd.node_type == "IDENTIFIER":
                                    columns.append(idd.value)
        return columns

    def _analyze_where_clause(self, where_node, table_names):
        if not table_names or not hasattr(where_node, 'children'):
            return
        line, col = self._safe_get_line_column(where_node)
        self.current_node_info = where_node
        for child in where_node.children:
            if child.node_type == "COMPARISON":
                self._analyze_comparison(child, table_names)
            elif child.node_type in ["AND_CONDITION", "OR_CONDITION", "NOT_CONDITION"]:
                self._analyze_where_clause(child, table_names)

    def _analyze_comparison(self, comp_node, table_names):
        column_name = None
        literal_type = None
        if not hasattr(comp_node, 'children'):
            return
        line, col = self._safe_get_line_column(comp_node)
        self.current_node_info = comp_node
        
        # Extract column and literal first
        for child in comp_node.children:
            if child.node_type == "IDENTIFIER":
                column_name = child.value
            elif child.node_type == "LITERAL":
                literal_type = child.data_type if hasattr(child, 'data_type') and child.data_type else self._infer_type(child.value)
        
        if column_name and literal_type:
            resolved = self._resolve_column_ambiguity(column_name, table_names)
            if resolved:
                col_type = resolved[1]
                if not self._types_compatible(col_type, literal_type):
                    self.add_error(
                        f"Type mismatch in comparison: column '{column_name}' is {col_type}, but compared with {literal_type}",
                        line, col
                    )

    def _analyze_update(self, node, annotated):
        table_name = None
        if not hasattr(node, 'children'):
            return
        
        # ✅ FIXED: Extract table name FIRST
        for child in node.children:
            if child.node_type == "IDENTIFIER" and table_name is None:
                table_name = child.value
        
        line, col = self._safe_get_line_column(node)
        
        # ✅ FIXED: Table existence FIRST
        if table_name and not self.symbol_table.table_exists(table_name):
            self.add_error(f"Table '{table_name}' does not exist", line, col)
            for child in node.children:
                annotated.add_child(self._analyze_node(child))
            return
        
        # Table exists - safe to analyze
        for child in node.children:
            annotated_child = self._analyze_node(child)
            annotated.add_child(annotated_child)
            if child.node_type == "WHERE_CLAUSE":
                self._analyze_where_clause(child, [table_name])

    def _analyze_delete(self, node, annotated):
        table_name = None
        if not hasattr(node, 'children'):
            return
        
        # ✅ FIXED: Extract table name FIRST
        for child in node.children:
            if child.node_type == "IDENTIFIER" and table_name is None:
                table_name = child.value
        
        line, col = self._safe_get_line_column(node)
        
        # ✅ FIXED: Table existence FIRST - CRITICAL FIX
        if table_name and not self.symbol_table.table_exists(table_name):
            self.add_error(f"Table '{table_name}' does not exist", line, col)
            # Still build tree but SKIP column/WHERE analysis
            for child in node.children:
                annotated.add_child(self._analyze_node(child))
            return
        
        # Table exists - safe to analyze WHERE
        for child in node.children:
            annotated_child = self._analyze_node(child)
            annotated.add_child(annotated_child)
            if child.node_type == "WHERE_CLAUSE":
                self._analyze_where_clause(child, [table_name])

    def _types_compatible(self, expected_type, actual_type):
        if not expected_type or not actual_type:
            return False
        type_map = {
            'INT': 'INT', 'INTEGER': 'INT', 'NUMBER': 'INT',
            'FLOAT': 'FLOAT', 'REAL': 'FLOAT', 'DOUBLE': 'FLOAT',
            'TEXT': 'TEXT', 'STRING': 'TEXT', 'VARCHAR': 'TEXT'
        }
        expected = type_map.get(str(expected_type).upper(), str(expected_type).upper())
        actual = type_map.get(str(actual_type).upper(), str(actual_type).upper())
        if expected in ['INT', 'FLOAT'] and actual in ['INT', 'FLOAT']:
            return True
        return expected == actual

    def _infer_type(self, value):
        if value is None:
            return 'TEXT'
        value_str = str(value)
        try:
            if '.' in value_str:
                float(value_str)
                return 'FLOAT'
            else:
                int(value_str)
                return 'INT'
        except ValueError:
            return 'TEXT'

    def add_error(self, message, line, column):
        self.errors.append({
            'message': message,
            'line': line if line else 0,
            'column': column if column else 0,
            'type': 'SEMANTIC_ERROR'
        })

    def get_errors(self):
        return self.errors

    def get_symbol_table(self):
        return self.symbol_table

    def is_successful(self):
        return self.success

    def get_success_message(self):
        if self.success:
            return "✅ Semantic Analysis Successful. Query is valid."
        else:
            return f"❌ Semantic Analysis Failed. {len(self.errors)} error(s) found."

    def get_results(self):
        results = {
            'success': len(self.errors) == 0,
            'symbol_table': self.symbol_table,
            'errors': self.errors,
            'annotated_tree': self.annotated_tree,
            'type': 'SemanticResults'
        }
        if results['success']:
            results['message'] = "Semantic Analysis Successful. Query is valid."
        else:
            results['message'] = f"Semantic Analysis Failed. {len(self.errors)} error(s) found."
        return results
