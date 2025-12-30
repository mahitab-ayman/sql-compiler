"""
Phase 02: Syntax Analyzer for SQL-like Language
"""
from compiler.lexer import Token, LexicalAnalyzer

class ParseTreeNode:
    """Represents a node in the parse tree"""
    def __init__(self, node_type, value=None, children=None, line=None, column=None):
        self.node_type = node_type
        self.value = value
        self.children = children if children is not None else []
        self.line = line
        self.column = column
        # Semantic annotations (for Phase 03)
        self.data_type = None
        self.symbol_ref = None

    def add_child(self, child):
        """Add a child node"""
        if child is not None:
            self.children.append(child)

    def has_error(self):
        """Check if this node or its children contain errors"""
        if self.node_type == 'ERROR':
            return True
        for child in self.children:
            if hasattr(child, 'has_error') and child.has_error():
                return True
        return False

    def __repr__(self):
        return f"ParseTreeNode({self.node_type}, {self.value}, {len(self.children)} children)"

    def to_string(self, indent=0):
        """Convert parse tree to string representation"""
        result = "  " * indent + f"{self.node_type}"
        if self.value:
            result += f" ({self.value})"
        if self.data_type:
            result += f" [type: {self.data_type}]"
        if self.symbol_ref:
            result += f" [ref: {self.symbol_ref}]"
        result += "\n"
        for child in self.children:
            result += child.to_string(indent + 1)
        return result

class SyntaxAnalyzer:
    """Syntax Analyzer using Recursive Descent Parsing"""

    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.errors = []
        self.parse_tree = None

    def current_token(self):
        """Get current token"""
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index]
        return None

    def peek_token(self, offset=1):
        """Peek at token ahead"""
        idx = self.current_index + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def advance(self):
        """Advance to next token"""
        if self.current_index < len(self.tokens):
            self.current_index += 1

    def match(self, expected_type, expected_value=None):
        """Match current token with expected type and optionally value"""
        token = self.current_token()
        if token is None:
            return False
        if token.token_type != expected_type:
            return False
        if expected_value is not None and token.lexeme != expected_value:
            return False
        return True

    def consume(self, expected_type, expected_value=None):
        """Consume token if it matches, otherwise report error and create error node"""
        token = self.current_token()
        if token is None:
            error_msg = f"Unexpected end of file. Expected {expected_type}" +                        (f" '{expected_value}'" if expected_value else "")
            self.report_error(error_msg)
            return None

        if token.token_type == expected_type:
            if expected_value is None or token.lexeme == expected_value:
                self.advance()
                return token
            else:
                error_msg = f"Expected '{expected_value}' but found '{token.lexeme}'"
                self.report_error(error_msg, token.line, token.column)
                return None
        else:
            error_msg = f"Expected {expected_type}" +                        (f" '{expected_value}'" if expected_value else "") +                        f" but found {token.token_type} '{token.lexeme}'"
            self.report_error(error_msg, token.line, token.column)
            return None

    def report_error(self, message, line=None, column=None):
        """Report a syntax error"""
        token = self.current_token()
        if token:
            line = line or token.line
            column = column or token.column
        self.errors.append({
            'type': 'Syntax Error',
            'message': message,
            'line': line or 1,
            'column': column or 1
        })

    def synchronize(self):
        """Error recovery: skip tokens until synchronizing point"""
        while self.current_index < len(self.tokens):
            token = self.current_token()
            if token is None:
                break
            # Synchronize on semicolon or major keywords
            if token.token_type == 'DELIMITER' and token.lexeme == ';':
                self.advance() # consume the semicolon
                return
            if token.token_type == 'KEYWORD' and token.lexeme in ['CREATE', 'INSERT', 'SELECT', 'UPDATE', 'DELETE']:
                return
            self.advance()

    def parse(self):
        """Main parsing method"""
        self.errors = []
        self.current_index = 0
        statements = []
        while self.current_index < len(self.tokens):
            token = self.current_token()
            if token is None or token.token_type == 'EOF':
                break
            # Skip extra semicolons between statements
            if token.token_type == 'DELIMITER' and token.lexeme == ';':
                self.advance()
                continue
            # Parse statement (this returns a STATEMENT node with semicolon child)
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else: # Error recovery
                self.synchronize()
        if statements:
            self.parse_tree = ParseTreeNode('PROGRAM', children=statements)
        else:
            self.parse_tree = ParseTreeNode('PROGRAM', children=[])
        return self.parse_tree

    def parse_statement(self):
        """Parse a SQL statement and its terminating semicolon"""
        token = self.current_token()
        if token is None:
            return None
        # Create a STATEMENT wrapper node
        stmt_node = ParseTreeNode('STATEMENT', line=token.line, column=token.column)
        # Parse the actual SQL command
        sql_cmd = None
        if token.token_type == 'KEYWORD':
            if token.lexeme == 'CREATE':
                sql_cmd = self.parse_create_table()
            elif token.lexeme == 'INSERT':
                sql_cmd = self.parse_insert()
            elif token.lexeme == 'SELECT':
                sql_cmd = self.parse_select()
            elif token.lexeme == 'UPDATE':
                sql_cmd = self.parse_update()
            elif token.lexeme == 'DELETE':
                sql_cmd = self.parse_delete()
        if not sql_cmd:
            self.report_error(f"Unexpected token '{token.lexeme}'. Expected a statement keyword.")
            return None
        # Add the SQL command as child
        stmt_node.add_child(sql_cmd)
        # *** CHECK FOR SEMICOLON - ONLY IF NO ERRORS IN SQL COMMAND ***
        if sql_cmd.has_error():
            # Command already has errors - synchronize without checking semicolon
            # This avoids duplicate error reporting
            self.synchronize()
        else:
            # Command parsed successfully - check for semicolon
            token = self.current_token()
            if token and not (token.token_type == 'EOF'):
                if self.match('DELIMITER', ';'):
                    # Found semicolon - add it to tree
                    semicolon_token = self.consume('DELIMITER', ';')
                    stmt_node.add_child(
                        ParseTreeNode('SEMICOLON', ';',
                                     line=semicolon_token.line,
                                     column=semicolon_token.column)
                    )
                else:
                    # Missing semicolon - add ERROR node to tree
                    error_node = ParseTreeNode(
                        'ERROR',
                        f"❌ MISSING SEMICOLON after statement (found '{token.lexeme}' instead)",
                        line=token.line,
                        column=token.column
                    )
                    stmt_node.add_child(error_node)
                    # Also report error
                    self.report_error(
                        f"Expected semicolon (;) after statement but found '{token.lexeme}'",
                        token.line, token.column
                    )
                    # Try to recover
                    self.synchronize()
        return stmt_node

    def parse_create_table(self):
        """Parse CREATE TABLE statement"""
        node = ParseTreeNode('CREATE_TABLE')
        # CREATE
        create_token = self.consume('KEYWORD', 'CREATE')
        if create_token:
            node.add_child(ParseTreeNode('KEYWORD', 'CREATE', line=create_token.line, column=create_token.column))
        else:
            return None
        # TABLE
        table_token = self.consume('KEYWORD', 'TABLE')
        if table_token:
            node.add_child(ParseTreeNode('KEYWORD', 'TABLE', line=table_token.line, column=table_token.column))
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING TABLE keyword after CREATE'))
            return node
        # Table name
        table_name = self.parse_identifier()
        if table_name:
            node.add_child(table_name)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING table name'))
            return node
        # (
        lparen = self.consume('DELIMITER', '(')
        if lparen:
            node.add_child(ParseTreeNode('DELIMITER', '(', line=lparen.line, column=lparen.column))
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING opening parenthesis'))
            return node
        # Column definitions
        columns = self.parse_column_list()
        if columns:
            node.add_child(columns)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING column definitions'))
            return node
        # )
        rparen = self.consume('DELIMITER', ')')
        if rparen:
            node.add_child(ParseTreeNode('DELIMITER', ')', line=rparen.line, column=rparen.column))
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING closing parenthesis'))
            return node
        return node

    def parse_column_list(self):
        """Parse list of column definitions"""
        node = ParseTreeNode('COLUMN_LIST')
        # First column
        col = self.parse_column_definition()
        if col:
            node.add_child(col)
        else:
            return None
        # Additional columns
        while self.match('DELIMITER', ','):
            comma = self.consume('DELIMITER', ',')
            node.add_child(ParseTreeNode('DELIMITER', ',', line=comma.line, column=comma.column))
            col = self.parse_column_definition()
            if col:
                node.add_child(col)
            else:
                break
        return node

    def parse_column_definition(self):
        """Parse a column definition: identifier type"""
        node = ParseTreeNode('COLUMN_DEFINITION')
        # Column name
        col_name = self.parse_identifier()
        if col_name:
            node.add_child(col_name)
        else:
            return None
        # Data type
        type_node = self.parse_data_type()
        if type_node:
            node.add_child(type_node)
        else:
            return None
        return node

    def parse_data_type(self):
        """Parse data type: INT, FLOAT, or TEXT"""
        token = self.current_token()
        if token and token.token_type == 'KEYWORD':
            if token.lexeme in ['INT', 'FLOAT', 'TEXT']:
                self.advance()
                return ParseTreeNode('DATA_TYPE', token.lexeme, line=token.line, column=token.column)
        self.report_error(f"Expected data type (INT, FLOAT, or TEXT) but found '{token.lexeme if token else 'EOF'}'")
        return None

    def parse_insert(self):
        """Parse INSERT INTO statement"""
        node = ParseTreeNode('INSERT')
        # INSERT
        insert_token = self.consume('KEYWORD', 'INSERT')
        if insert_token:
            node.add_child(ParseTreeNode('KEYWORD', 'INSERT', line=insert_token.line, column=insert_token.column))
        else:
            return None
        # INTO
        into_token = self.consume('KEYWORD', 'INTO')
        if into_token:
            node.add_child(ParseTreeNode('KEYWORD', 'INTO', line=into_token.line, column=into_token.column))
        else:
            token = self.current_token()
            node.add_child(ParseTreeNode('ERROR',
                f"❌ MISSING INTO keyword after INSERT (found '{token.lexeme if token else 'EOF'}' instead)",
                line=token.line if token else 0, column=token.column if token else 0))
            return node
        # Table name
        table_name = self.parse_identifier()
        if table_name:
            node.add_child(table_name)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING table name'))
            return node
        # Optional column list
        if self.match('DELIMITER', '('):
            lparen = self.consume('DELIMITER', '(')
            node.add_child(ParseTreeNode('DELIMITER', '(', line=lparen.line, column=lparen.column))
            columns = self.parse_identifier_list()
            if columns:
                node.add_child(columns)
            rparen = self.consume('DELIMITER', ')')
            if rparen:
                node.add_child(ParseTreeNode('DELIMITER', ')', line=rparen.line, column=rparen.column))
            else:
                node.add_child(ParseTreeNode('ERROR', '❌ MISSING closing parenthesis'))
                return node
        # VALUES
        values_token = self.consume('KEYWORD', 'VALUES')
        if values_token:
            node.add_child(ParseTreeNode('KEYWORD', 'VALUES', line=values_token.line, column=values_token.column))
        else:
            token = self.current_token()
            node.add_child(ParseTreeNode('ERROR',
                f"❌ MISSING VALUES keyword (found '{token.lexeme if token else 'EOF'}' instead)",
                line=token.line if token else 0, column=token.column if token else 0))
            return node
        # Value list
        value_list = self.parse_value_list()
        if value_list:
            node.add_child(value_list)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING value list'))
            return node
        return node

    def parse_select(self):
        """Parse SELECT statement - supports FROM table1, table2"""
        node = ParseTreeNode('SELECT')
        # SELECT
        select_token = self.consume('KEYWORD', 'SELECT')
        if select_token:
            node.add_child(ParseTreeNode('KEYWORD', 'SELECT', line=select_token.line, column=select_token.column))
        else:
            return None
        # Select list
        select_list = self.parse_select_list()
        if select_list:
            node.add_child(select_list)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING column list or *'))
            return node
        # FROM (REQUIRED)
        token = self.current_token()
        if self.match('KEYWORD', 'FROM'):
            from_token = self.consume('KEYWORD', 'FROM')
            node.add_child(ParseTreeNode('KEYWORD', 'FROM', line=from_token.line, column=from_token.column))
        else:
            # Missing FROM - add ERROR node
            node.add_child(ParseTreeNode('ERROR',
                f"❌ MISSING FROM keyword (found '{token.lexeme if token else 'EOF'}' instead)",
                line=token.line if token else 0, column=token.column if token else 0))
            self.report_error(
                f"Expected FROM keyword but found '{token.lexeme if token else 'EOF'}'",
                token.line if token else 0, token.column if token else 0
            )
            return node
        # ✅ NEW: Table list (supports multiple tables: FROM a, b, c)
        table_list = self.parse_table_list()
        if table_list:
            node.add_child(table_list)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING table name after FROM'))
            return node
        # Optional WHERE clause
        if self.match('KEYWORD', 'WHERE'):
            where_clause = self.parse_where_clause()
            if where_clause:
                node.add_child(where_clause)
        return node

    def parse_table_list(self):
        """✅ NEW: Parse comma-separated table list: a, b, c"""
        node = ParseTreeNode('TABLE_LIST')
        # First table
        table_name = self.parse_identifier()
        if table_name:
            node.add_child(table_name)
        else:
            return None
        # Additional tables (optional)
        while self.match('DELIMITER', ','):
            comma = self.consume('DELIMITER', ',')
            node.add_child(ParseTreeNode('DELIMITER', ',', line=comma.line, column=comma.column))
            table_name = self.parse_identifier()
            if table_name:
                node.add_child(table_name)
            else:
                break
        return node

    def parse_select_list(self):
        """Parse SELECT list (columns or *)"""
        node = ParseTreeNode('SELECT_LIST')
        if self.match('OPERATOR', '*'):
            star_token = self.consume('OPERATOR', '*')
            if star_token:
                node.add_child(ParseTreeNode('OPERATOR', '*', line=star_token.line, column=star_token.column))
        else:
            id_list = self.parse_identifier_list()
            if id_list:
                node.add_child(id_list)
            else:
                return None
        return node

    def parse_update(self):
        """Parse UPDATE statement"""
        node = ParseTreeNode('UPDATE')
        # UPDATE
        update_token = self.consume('KEYWORD', 'UPDATE')
        if update_token:
            node.add_child(ParseTreeNode('KEYWORD', 'UPDATE', line=update_token.line, column=update_token.column))
        else:
            return None
        # Table name
        table_name = self.parse_identifier()
        if table_name:
            node.add_child(table_name)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING table name'))
            return node
        # SET
        set_token = self.consume('KEYWORD', 'SET')
        if set_token:
            node.add_child(ParseTreeNode('KEYWORD', 'SET', line=set_token.line, column=set_token.column))
        else:
            token = self.current_token()
            node.add_child(ParseTreeNode('ERROR',
                f"❌ MISSING SET keyword (found '{token.lexeme if token else 'EOF'}' instead)",
                line=token.line if token else 0, column=token.column if token else 0))
            return node
        # Assignment list
        assignments = self.parse_assignment_list()
        if assignments:
            node.add_child(assignments)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING assignment list'))
            return node
        # Optional WHERE clause
        if self.match('KEYWORD', 'WHERE'):
            where_clause = self.parse_where_clause()
            if where_clause:
                node.add_child(where_clause)
        return node

    def parse_delete(self):
        """Parse DELETE statement"""
        node = ParseTreeNode('DELETE')
        # DELETE
        delete_token = self.consume('KEYWORD', 'DELETE')
        if delete_token:
            node.add_child(ParseTreeNode('KEYWORD', 'DELETE', line=delete_token.line, column=delete_token.column))
        else:
            return None
        # FROM
        token = self.current_token()
        if self.match('KEYWORD', 'FROM'):
            from_token = self.consume('KEYWORD', 'FROM')
            node.add_child(ParseTreeNode('KEYWORD', 'FROM', line=from_token.line, column=from_token.column))
        else:
            node.add_child(ParseTreeNode('ERROR',
                f"❌ MISSING FROM keyword after DELETE (found '{token.lexeme if token else 'EOF'}' instead)",
                line=token.line if token else 0, column=token.column if token else 0))
            return node
        # Table name
        table_name = self.parse_identifier()
        if table_name:
            node.add_child(table_name)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING table name'))
            return node
        # Optional WHERE clause
        if self.match('KEYWORD', 'WHERE'):
            where_clause = self.parse_where_clause()
            if where_clause:
                node.add_child(where_clause)
        return node

    def parse_where_clause(self):
        """Parse WHERE clause with conditions"""
        node = ParseTreeNode('WHERE_CLAUSE')
        # WHERE
        where_token = self.consume('KEYWORD', 'WHERE')
        if where_token:
            node.add_child(ParseTreeNode('KEYWORD', 'WHERE', line=where_token.line, column=where_token.column))
        else:
            return None
        # Condition
        condition = self.parse_condition()
        if condition:
            node.add_child(condition)
        else:
            node.add_child(ParseTreeNode('ERROR', '❌ MISSING condition after WHERE'))
        return node

    def parse_condition(self):
        """Parse condition with AND, OR, NOT support"""
        # Parse NOT conditions
        if self.match('KEYWORD', 'NOT'):
            node = ParseTreeNode('NOT_CONDITION')
            not_token = self.consume('KEYWORD', 'NOT')
            node.add_child(ParseTreeNode('KEYWORD', 'NOT', line=not_token.line, column=not_token.column))
            # Parse nested condition
            nested = self.parse_condition()
            if nested:
                node.add_child(nested)
            else:
                return None
            return node
        # Parse base condition
        left = self.parse_simple_condition()
        if not left:
            return None
        # Check for AND/OR
        while self.match('KEYWORD', 'AND') or self.match('KEYWORD', 'OR'):
            op_token = self.current_token()
            op = op_token.lexeme
            self.advance()
            node = ParseTreeNode(f'{op}_CONDITION')
            node.add_child(left)
            node.add_child(ParseTreeNode('KEYWORD', op, line=op_token.line, column=op_token.column))
            right = self.parse_simple_condition()
            if not right:
                return None
            node.add_child(right)
            left = node
        return left

    def parse_simple_condition(self):
        """Parse a simple comparison condition"""
        # Handle parentheses
        if self.match('DELIMITER', '('):
            lparen = self.consume('DELIMITER', '(')
            condition = self.parse_condition()
            rparen = self.consume('DELIMITER', ')')
            if not rparen:
                return None
            return condition
        node = ParseTreeNode('COMPARISON')
        # Left operand (identifier or literal)
        left = self.parse_expression()
        if not left:
            return None
        node.add_child(left)
        # Operator
        op_token = self.current_token()
        if op_token and op_token.token_type == 'OPERATOR':
            if op_token.lexeme in ['=', '<', '>', '<=', '>=', '<>', '!=']:
                self.advance()
                node.add_child(ParseTreeNode('OPERATOR', op_token.lexeme, line=op_token.line, column=op_token.column))
            else:
                self.report_error(f"Expected comparison operator but found '{op_token.lexeme}'",
                                 op_token.line, op_token.column)
                return None
        else:
            self.report_error("Expected comparison operator", op_token.line if op_token else 1,
                             op_token.column if op_token else 1)
            return None
        # Right operand
        right = self.parse_expression()
        if not right:
            return None
        node.add_child(right)
        return node

    def parse_expression(self):
        """Parse an expression (identifier or literal)"""
        token = self.current_token()
        if token is None:
            return None
        if token.token_type == 'IDENTIFIER':
            self.advance()
            return ParseTreeNode('IDENTIFIER', token.lexeme, line=token.line, column=token.column)
        elif token.token_type in ['INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL']:
            self.advance()
            node = ParseTreeNode('LITERAL', token.lexeme,
                                line=token.line, column=token.column)
            node.data_type = token.token_type.replace('_LITERAL', '')
            return node
        else:
            return None

    def parse_identifier_list(self):
        """Parse a list of identifiers"""
        node = ParseTreeNode('IDENTIFIER_LIST')
        # First identifier
        id_node = self.parse_identifier()
        if id_node:
            node.add_child(id_node)
        else:
            return None
        # Additional identifiers
        while self.match('DELIMITER', ','):
            comma = self.consume('DELIMITER', ',')
            node.add_child(ParseTreeNode('DELIMITER', ',', line=comma.line, column=comma.column))
            id_node = self.parse_identifier()
            if id_node:
                node.add_child(id_node)
            else:
                break
        return node

    def parse_identifier(self):
        """Parse an identifier"""
        token = self.current_token()
        if token and token.token_type == 'IDENTIFIER':
            self.advance()
            return ParseTreeNode('IDENTIFIER', token.lexeme, line=token.line, column=token.column)
        self.report_error(f"Expected identifier but found '{token.lexeme if token else 'EOF'}'")
        return None

    def parse_value_list(self):
        """Parse a list of values"""
        node = ParseTreeNode('VALUE_LIST')
        # (
        lparen = self.consume('DELIMITER', '(')
        if lparen:
            node.add_child(ParseTreeNode('DELIMITER', '(', line=lparen.line, column=lparen.column))
        else:
            return None
        # First value
        value = self.parse_expression()
        if value:
            node.add_child(value)
        else:
            return None
        # Additional values
        while self.match('DELIMITER', ','):
            comma = self.consume('DELIMITER', ',')
            node.add_child(ParseTreeNode('DELIMITER', ',', line=comma.line, column=comma.column))
            value = self.parse_expression()
            if value:
                node.add_child(value)
            else:
                break
        # )
        rparen = self.consume('DELIMITER', ')')
        if rparen:
            node.add_child(ParseTreeNode('DELIMITER', ')', line=rparen.line, column=rparen.column))
        else:
            return None
        return node

    def parse_assignment_list(self):
        """Parse assignment list for UPDATE SET clause"""
        node = ParseTreeNode('ASSIGNMENT_LIST')
        # First assignment
        assignment = self.parse_assignment()
        if assignment:
            node.add_child(assignment)
        else:
            return None
        # Additional assignments
        while self.match('DELIMITER', ','):
            comma = self.consume('DELIMITER', ',')
            node.add_child(ParseTreeNode('DELIMITER', ',', line=comma.line, column=comma.column))
            assignment = self.parse_assignment()
            if assignment:
                node.add_child(assignment)
            else:
                break
        return node

    def parse_assignment(self):
        """Parse a single assignment: identifier = expression"""
        node = ParseTreeNode('ASSIGNMENT')
        # Identifier
        id_node = self.parse_identifier()
        if id_node:
            node.add_child(id_node)
        else:
            return None
        # =
        eq_token = self.consume('OPERATOR', '=')
        if eq_token:
            node.add_child(ParseTreeNode('OPERATOR', '=', line=eq_token.line, column=eq_token.column))
        else:
            return None
        # Expression
        expr = self.parse_expression()
        if expr:
            node.add_child(expr)
        else:
            return None
        return node

    def get_parse_tree(self):
        """Get the parse tree"""
        return self.parse_tree

    def get_errors(self):
        """Get syntax errors"""
        return self.errors

    def print_parse_tree(self):
        """Print the parse tree"""
        print("=" * 60)
        print("SYNTAX ANALYSIS OUTPUT")
        print("=" * 60)
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  {error['type']}: {error['message']} at line {error['line']}, position {error['column']}")
            print()
        if self.parse_tree:
            print("\nPARSE TREE:")
            print(self.parse_tree.to_string())
        else:
            print("\nNo parse tree generated.")
        print("=" * 60)
