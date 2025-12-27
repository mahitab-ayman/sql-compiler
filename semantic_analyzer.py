"""
Phase 03: Semantic Analyzer for SQL-like Language
Performs type checking, scope validation, and semantic analysis
"""

from parser import ParseTreeNode


class ColumnInfo:
    """Represents information about a column"""
    def __init__(self, name, data_type, line=None, column=None):
        self.name = name
        self.data_type = data_type  # INT, FLOAT, TEXT
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Column({self.name}, {self.data_type})"


class TableInfo:
    """Represents information about a table"""
    def __init__(self, name, line=None, column=None):
        self.name = name
        self.columns = {}  # Dictionary mapping column name to ColumnInfo
        self.line = line
        self.column = column
    
    def add_column(self, column_info):
        """Add a column to the table"""
        self.columns[column_info.name] = column_info
    
    def get_column(self, column_name):
        """Get column information by name"""
        return self.columns.get(column_name)
    
    def __repr__(self):
        return f"Table({self.name}, {len(self.columns)} columns)"


class SymbolTable:
    """Manages symbol table for tables and columns"""
    def __init__(self):
        self.tables = {}  # Dictionary mapping table name to TableInfo
    
    def add_table(self, table_info):
        """Add a table to the symbol table"""
        self.tables[table_info.name] = table_info
    
    def get_table(self, table_name):
        """Get table information by name"""
        return self.tables.get(table_name)
    
    def table_exists(self, table_name):
        """Check if a table exists"""
        return table_name in self.tables
    
    def get_column_info(self, table_name, column_name):
        """Get column information from a specific table"""
        table = self.get_table(table_name)
        if table:
            return table.get_column(column_name)
        return None
    
    def dump(self):
        """Dump the symbol table contents"""
        result = []
        result.append("=" * 60)
        result.append("SYMBOL TABLE")
        result.append("=" * 60)
        
        if not self.tables:
            result.append("(Empty)")
        else:
            for table_name, table_info in self.tables.items():
                result.append(f"\nTable: {table_name}")
                result.append(f"  Columns:")
                for col_name, col_info in table_info.columns.items():
                    result.append(f"    - {col_name}: {col_info.data_type}")
        
        result.append("\n" + "=" * 60)
        return "\n".join(result)


class SemanticAnalyzer:
    """Semantic Analyzer for SQL-like language"""
    
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_table_context = None  # For resolving column references
    
    def analyze(self):
        """Main semantic analysis method"""
        self.errors = []
        
        if not self.parse_tree or self.parse_tree.node_type != 'PROGRAM':
            self.errors.append({
                'type': 'Semantic Error',
                'message': "Invalid parse tree: expected PROGRAM node",
                'line': 1,
                'column': 1
            })
            return False
        
        # Process all statements
        for statement in self.parse_tree.children:
            if statement.node_type == 'CREATE_TABLE':
                self.analyze_create_table(statement)
            elif statement.node_type == 'INSERT':
                self.analyze_insert(statement)
            elif statement.node_type == 'SELECT':
                self.analyze_select(statement)
            elif statement.node_type == 'UPDATE':
                self.analyze_update(statement)
            elif statement.node_type == 'DELETE':
                self.analyze_delete(statement)
        
        return len(self.errors) == 0
    
    def analyze_create_table(self, node):
        """Analyze CREATE TABLE statement"""
        # Extract table name
        table_name_node = None
        for child in node.children:
            if child.node_type == 'IDENTIFIER' and child.value:
                table_name_node = child
                break
        
        if not table_name_node:
            self.errors.append({
                'type': 'Semantic Error',
                'message': "CREATE TABLE: Missing table name",
                'line': node.line or 1,
                'column': node.column or 1
            })
            return
        
        table_name = table_name_node.value
        
        # Check for redeclaration
        if self.symbol_table.table_exists(table_name):
            self.errors.append({
                'type': 'Semantic Error',
                'message': f"Table '{table_name}' already exists. Redeclaration is not allowed.",
                'line': table_name_node.line or 1,
                'column': table_name_node.column or 1
            })
            return
        
        # Create table info
        table_info = TableInfo(table_name, line=table_name_node.line, column=table_name_node.column)
        
        # Extract column definitions
        column_list_node = None
        for child in node.children:
            if child.node_type == 'COLUMN_LIST':
                column_list_node = child
                break
        
        if not column_list_node:
            self.errors.append({
                'type': 'Semantic Error',
                'message': "CREATE TABLE: Missing column definitions",
                'line': node.line or 1,
                'column': node.column or 1
            })
            return
        
        # Process each column definition
        for col_def in column_list_node.children:
            if col_def.node_type != 'COLUMN_DEFINITION':
                continue
            
            col_name_node = None
            col_type_node = None
            
            for child in col_def.children:
                if child.node_type == 'IDENTIFIER':
                    col_name_node = child
                elif child.node_type == 'DATA_TYPE':
                    col_type_node = child
            
            if not col_name_node or not col_type_node:
                continue
            
            col_name = col_name_node.value
            col_type = col_type_node.value
            
            # Validate data type
            if col_type not in ['INT', 'FLOAT', 'TEXT']:
                self.errors.append({
                    'type': 'Semantic Error',
                    'message': f"Invalid data type '{col_type}'. Expected INT, FLOAT, or TEXT.",
                    'line': col_type_node.line or 1,
                    'column': col_type_node.column or 1
                })
                continue
            
            # Create column info
            col_info = ColumnInfo(col_name, col_type, 
                                 line=col_name_node.line, column=col_name_node.column)
            table_info.add_column(col_info)
            
            # Annotate parse tree
            col_name_node.data_type = col_type
            col_name_node.symbol_ref = f"{table_name}.{col_name}"
        
        # Add table to symbol table
        self.symbol_table.add_table(table_info)
        
        # Annotate table name node
        table_name_node.symbol_ref = f"table:{table_name}"
    
    def analyze_insert(self, node):
        """Analyze INSERT INTO statement"""
        # Extract table name
        table_name_node = None
        for child in node.children:
            if child.node_type == 'IDENTIFIER' and child.value:
                table_name_node = child
                break
        
        if not table_name_node:
            self.errors.append({
                'type': 'Semantic Error',
                'message': "INSERT: Missing table name",
                'line': node.line or 1,
                'column': node.column or 1
            })
            return
        
        table_name = table_name_node.value
        
        # Check table existence
        if not self.symbol_table.table_exists(table_name):
            self.errors.append({
                'type': 'Semantic Error',
                'message': f"Table '{table_name}' does not exist.",
                'line': table_name_node.line or 1,
                'column': table_name_node.column or 1
            })
            return
        
        table_info = self.symbol_table.get_table(table_name)
        table_name_node.symbol_ref = f"table:{table_name}"
        
        # Get column list (if specified) or use all columns
        specified_columns = []
        column_list_node = None
        for child in node.children:
            if child.node_type == 'IDENTIFIER_LIST':
                column_list_node = child
                break
        
        if column_list_node:
            # Use specified columns
            for col_node in column_list_node.children:
                if col_node.node_type == 'IDENTIFIER':
                    col_name = col_node.value
                    col_info = table_info.get_column(col_name)
                    if not col_info:
                        self.errors.append({
                            'type': 'Semantic Error',
                            'message': f"Column '{col_name}' does not exist in table '{table_name}'.",
                            'line': col_node.line or 1,
                            'column': col_node.column or 1
                        })
                        return
                    specified_columns.append((col_name, col_info))
                    col_node.symbol_ref = f"{table_name}.{col_name}"
                    col_node.data_type = col_info.data_type
        else:
            # Use all columns in order
            specified_columns = [(name, info) for name, info in table_info.columns.items()]
        
        # Get value list
        value_list_node = None
        for child in node.children:
            if child.node_type == 'VALUE_LIST':
                value_list_node = child
                break
        
        if not value_list_node:
            self.errors.append({
                'type': 'Semantic Error',
                'message': "INSERT: Missing VALUES clause",
                'line': node.line or 1,
                'column': node.column or 1
            })
            return
        
        # Check value count
        values = [child for child in value_list_node.children 
                 if child.node_type in ['LITERAL', 'IDENTIFIER']]
        
        if len(values) != len(specified_columns):
            self.errors.append({
                'type': 'Semantic Error',
                'message': f"Type mismatch: Expected {len(specified_columns)} values but found {len(values)}.",
                'line': value_list_node.line or 1,
                'column': value_list_node.column or 1
            })
            return
        
        # Check type compatibility
        for i, (value_node, (col_name, col_info)) in enumerate(zip(values, specified_columns)):
            value_type = self.get_literal_type(value_node)
            
            if value_type is None:
                self.errors.append({
                    'type': 'Semantic Error',
                    'message': f"Invalid value type in VALUES list.",
                    'line': value_node.line or 1,
                    'column': value_node.column or 1
                })
                continue
            
            # Check type compatibility
            if not self.is_type_compatible(value_type, col_info.data_type):
                self.errors.append({
                    'type': 'Semantic Error',
                    'message': f"Type mismatch at position {i+1}: Column '{col_name}' is {col_info.data_type}, but {value_type} literal was provided.",
                    'line': value_node.line or 1,
                    'column': value_node.column or 1
                })
            else:
                # Annotate parse tree
                value_node.data_type = col_info.data_type
    
    def analyze_select(self, node):
        """Analyze SELECT statement"""
        # Extract table name
        table_name_node = None
        found_from = False
        for child in node.children:
            if child.node_type == 'KEYWORD' and child.value == 'FROM':
                found_from = True
            elif found_from and child.node_type == 'IDENTIFIER':
                table_name_node = child
                break
        
        if not table_name_node:
            self.errors.append({
                'type': 'Semantic Error',
                'message': "SELECT: Missing table name in FROM clause",
                'line': node.line or 1,
                'column': node.column or 1
            })
            return
        
        table_name = table_name_node.value
        
        # Check table existence
        if not self.symbol_table.table_exists(table_name):
            self.errors.append({
                'type': 'Semantic Error',
                'message': f"Table '{table_name}' does not exist.",
                'line': table_name_node.line or 1,
                'column': table_name_node.column or 1
            })
            return
        
        table_info = self.symbol_table.get_table(table_name)
        table_name_node.symbol_ref = f"table:{table_name}"
        self.current_table_context = table_name
        
        # Analyze SELECT list
        select_list_node = None
        for child in node.children:
            if child.node_type == 'SELECT_LIST':
                select_list_node = child
                break
        
        if select_list_node:
            # Check if it's SELECT *
            if select_list_node.children and select_list_node.children[0].node_type == 'OPERATOR' and \
               select_list_node.children[0].value == '*':
                # SELECT * - all columns are valid
                pass
            else:
                # Check each column in SELECT list
                id_list_node = None
                for child in select_list_node.children:
                    if child.node_type == 'IDENTIFIER_LIST':
                        id_list_node = child
                        break
                
                if id_list_node:
                    for col_node in id_list_node.children:
                        if col_node.node_type == 'IDENTIFIER':
                            col_name = col_node.value
                            col_info = table_info.get_column(col_name)
                            if not col_info:
                                self.errors.append({
                                    'type': 'Semantic Error',
                                    'message': f"Column '{col_name}' does not exist in table '{table_name}'.",
                                    'line': col_node.line or 1,
                                    'column': col_node.column or 1
                                })
                            else:
                                col_node.symbol_ref = f"{table_name}.{col_name}"
                                col_node.data_type = col_info.data_type
        
        # Analyze WHERE clause if present
        where_clause_node = None
        for child in node.children:
            if child.node_type == 'WHERE_CLAUSE':
                where_clause_node = child
                break
        
        if where_clause_node:
            self.analyze_where_clause(where_clause_node, table_info)
        
        self.current_table_context = None
    
    def analyze_update(self, node):
        """Analyze UPDATE statement"""
        # Extract table name
        table_name_node = None
        for child in node.children:
            if child.node_type == 'IDENTIFIER' and child.value:
                table_name_node = child
                break
        
        if not table_name_node:
            self.errors.append({
                'type': 'Semantic Error',
                'message': "UPDATE: Missing table name",
                'line': node.line or 1,
                'column': node.column or 1
            })
            return
        
        table_name = table_name_node.value
        
        # Check table existence
        if not self.symbol_table.table_exists(table_name):
            self.errors.append({
                'type': 'Semantic Error',
                'message': f"Table '{table_name}' does not exist.",
                'line': table_name_node.line or 1,
                'column': table_name_node.column or 1
            })
            return
        
        table_info = self.symbol_table.get_table(table_name)
        table_name_node.symbol_ref = f"table:{table_name}"
        self.current_table_context = table_name
        
        # Analyze SET clause
        assignment_list_node = None
        for child in node.children:
            if child.node_type == 'ASSIGNMENT_LIST':
                assignment_list_node = child
                break
        
        if assignment_list_node:
            for assignment_node in assignment_list_node.children:
                if assignment_node.node_type == 'ASSIGNMENT':
                    # Get column name
                    col_node = None
                    value_node = None
                    for child in assignment_node.children:
                        if child.node_type == 'IDENTIFIER':
                            col_node = child
                        elif child.node_type in ['LITERAL', 'IDENTIFIER']:
                            value_node = child
                    
                    if col_node and value_node:
                        col_name = col_node.value
                        col_info = table_info.get_column(col_name)
                        
                        if not col_info:
                            self.errors.append({
                                'type': 'Semantic Error',
                                'message': f"Column '{col_name}' does not exist in table '{table_name}'.",
                                'line': col_node.line or 1,
                                'column': col_node.column or 1
                            })
                        else:
                            col_node.symbol_ref = f"{table_name}.{col_name}"
                            col_node.data_type = col_info.data_type
                            
                            # Check type compatibility
                            value_type = self.get_literal_type(value_node)
                            if value_type and not self.is_type_compatible(value_type, col_info.data_type):
                                self.errors.append({
                                    'type': 'Semantic Error',
                                    'message': f"Type mismatch: Column '{col_name}' is {col_info.data_type}, but {value_type} literal was provided.",
                                    'line': value_node.line or 1,
                                    'column': value_node.column or 1
                                })
                            else:
                                value_node.data_type = col_info.data_type
        
        # Analyze WHERE clause if present
        where_clause_node = None
        for child in node.children:
            if child.node_type == 'WHERE_CLAUSE':
                where_clause_node = child
                break
        
        if where_clause_node:
            self.analyze_where_clause(where_clause_node, table_info)
        
        self.current_table_context = None
    
    def analyze_delete(self, node):
        """Analyze DELETE statement"""
        # Extract table name
        table_name_node = None
        found_from = False
        for child in node.children:
            if child.node_type == 'KEYWORD' and child.value == 'FROM':
                found_from = True
            elif found_from and child.node_type == 'IDENTIFIER':
                table_name_node = child
                break
        
        if not table_name_node:
            self.errors.append({
                'type': 'Semantic Error',
                'message': "DELETE: Missing table name in FROM clause",
                'line': node.line or 1,
                'column': node.column or 1
            })
            return
        
        table_name = table_name_node.value
        
        # Check table existence
        if not self.symbol_table.table_exists(table_name):
            self.errors.append({
                'type': 'Semantic Error',
                'message': f"Table '{table_name}' does not exist.",
                'line': table_name_node.line or 1,
                'column': table_name_node.column or 1
            })
            return
        
        table_info = self.symbol_table.get_table(table_name)
        table_name_node.symbol_ref = f"table:{table_name}"
        self.current_table_context = table_name
        
        # Analyze WHERE clause if present
        where_clause_node = None
        for child in node.children:
            if child.node_type == 'WHERE_CLAUSE':
                where_clause_node = child
                break
        
        if where_clause_node:
            self.analyze_where_clause(where_clause_node, table_info)
        
        self.current_table_context = None
    
    def analyze_where_clause(self, where_node, table_info):
        """Analyze WHERE clause conditions"""
        # Find condition node
        condition_node = None
        for child in where_node.children:
            if child.node_type not in ['KEYWORD']:
                condition_node = child
                break
        
        if condition_node:
            self.analyze_condition(condition_node, table_info)
    
    def analyze_condition(self, condition_node, table_info):
        """Recursively analyze condition nodes"""
        if condition_node.node_type == 'COMPARISON':
            # Analyze comparison: left op right
            operands = [child for child in condition_node.children 
                       if child.node_type in ['IDENTIFIER', 'LITERAL']]
            
            if len(operands) >= 2:
                left = operands[0]
                right = operands[1]
                
                # Analyze left operand
                if left.node_type == 'IDENTIFIER':
                    col_name = left.value
                    col_info = table_info.get_column(col_name)
                    if not col_info:
                        self.errors.append({
                            'type': 'Semantic Error',
                            'message': f"Column '{col_name}' does not exist in table '{table_info.name}'.",
                            'line': left.line or 1,
                            'column': left.column or 1
                        })
                    else:
                        left.symbol_ref = f"{table_info.name}.{col_name}"
                        left.data_type = col_info.data_type
                
                # Analyze right operand
                if right.node_type == 'LITERAL':
                    right_type = self.get_literal_type(right)
                    if right_type:
                        right.data_type = right_type
                
                # Check type compatibility
                if left.data_type and right.data_type:
                    if not self.is_type_compatible(left.data_type, right.data_type):
                        self.errors.append({
                            'type': 'Semantic Error',
                            'message': f"Type mismatch in comparison: {left.data_type} is not compatible with {right.data_type}.",
                            'line': condition_node.line or left.line or 1,
                            'column': condition_node.column or left.column or 1
                        })
        
        elif condition_node.node_type in ['AND_CONDITION', 'OR_CONDITION', 'NOT_CONDITION']:
            # Recursively analyze nested conditions
            for child in condition_node.children:
                if child.node_type not in ['KEYWORD']:
                    self.analyze_condition(child, table_info)
    
    def get_literal_type(self, node):
        """Get the data type of a literal node"""
        if node.node_type == 'LITERAL':
            if node.data_type:
                return node.data_type
            
            # Infer from value
            value = node.value
            if value.startswith("'") and value.endswith("'"):
                return 'TEXT'
            elif '.' in value:
                try:
                    float(value)
                    return 'FLOAT'
                except ValueError:
                    return None
            else:
                try:
                    int(value)
                    return 'INT'
                except ValueError:
                    return None
        
        return None
    
    def is_type_compatible(self, value_type, column_type):
        """Check if value type is compatible with column type"""
        # Map token types to semantic types
        type_map = {
            'INT': 'INT',
            'INT_LITERAL': 'INT',
            'FLOAT': 'FLOAT',
            'FLOAT_LITERAL': 'FLOAT',
            'TEXT': 'TEXT',
            'STRING_LITERAL': 'TEXT'
        }
        
        normalized_value_type = type_map.get(value_type, value_type)
        normalized_column_type = type_map.get(column_type, column_type)
        
        # INT can be compared with FLOAT (numeric compatibility)
        if normalized_value_type == 'INT' and normalized_column_type == 'FLOAT':
            return True
        if normalized_value_type == 'FLOAT' and normalized_column_type == 'INT':
            return True
        
        return normalized_value_type == normalized_column_type
    
    def get_errors(self):
        """Get semantic errors"""
        return self.errors
    
    def get_symbol_table(self):
        """Get the symbol table"""
        return self.symbol_table
    
    def print_results(self):
        """Print semantic analysis results"""
        print("=" * 60)
        print("SEMANTIC ANALYSIS OUTPUT")
        print("=" * 60)
        
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  {error['type']}: {error['message']} at line {error['line']}, position {error['column']}")
            print()
            print("Semantic Analysis Failed. Query is invalid.")
        else:
            print("\n✓ Semantic Analysis Successful. Query is valid.\n")
            print(self.symbol_table.dump())
            print("\nANNOTATED PARSE TREE:")
            if self.parse_tree:
                print(self.parse_tree.to_string())
        
        print("=" * 60)

