"""
Phase 01: Lexical Analyzer for SQL-like Language
Handles tokenization, error detection, and comment processing
"""

class Token:
    """Represents a token with type, lexeme, line, and column information"""
    def __init__(self, token_type, lexeme, line, column):
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.token_type}, '{self.lexeme}', {self.line}, {self.column})"
    
    def __str__(self):
        return f"<{self.token_type}, '{self.lexeme}', {self.line}, {self.column}>"


class LexicalAnalyzer:
    """Lexical Analyzer for SQL-like language"""
    
    # Keywords (case-sensitive)
    KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 
        'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE', 'INT', 
        'FLOAT', 'TEXT', 'AND', 'OR', 'NOT'
    }
    
    # Operators
    OPERATORS = {
        '=', '<', '>', '<=', '>=', '<>', '!=',
        '+', '-', '*', '/', '%'
    }
    
    # Delimiters
    DELIMITERS = {
        '(', ')', ',', ';', '.'
    }
    
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.current_pos = 0
        self.current_line = 1
        self.current_column = 1
        self.errors = []
        self.eof_reached = False
    
    def peek(self, offset=0):
        """Peek at character at current position + offset"""
        pos = self.current_pos + offset
        if pos >= len(self.source_code):
            return None
        return self.source_code[pos]
    
    def advance(self):
        """Advance to next character"""
        if self.current_pos >= len(self.source_code):
            self.eof_reached = True
            return None
        
        char = self.source_code[self.current_pos]
        self.current_pos += 1
        
        if char == '\n':
            self.current_line += 1
            self.current_column = 1
        else:
            self.current_column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.current_pos < len(self.source_code):
            char = self.source_code[self.current_pos]
            if char in ' \t\r':
                self.advance()
            else:
                break
    
    def handle_single_line_comment(self):
        """Handle single-line comments starting with --"""
        start_line = self.current_line
        start_column = self.current_column
        
        # Skip --
        self.advance()
        self.advance()
        
        # Skip until end of line
        while self.current_pos < len(self.source_code):
            char = self.source_code[self.current_pos]
            if char == '\n':
                self.advance()
                break
            self.advance()
    
    def handle_multi_line_comment(self):
        """Handle multi-line comments starting and ending with ##"""
        start_line = self.current_line
        start_column = self.current_column
        
        # Skip first #
        self.advance()
        
        # Check for second #
        if self.peek() != '#':
            self.errors.append({
                'type': 'Lexical Error',
                'message': f"Invalid character '#' at line {start_line}, position {start_column}. Expected '##' for multi-line comment.",
                'line': start_line,
                'column': start_column
            })
            return
        
        # Skip second #
        self.advance()
        
        # Look for closing ##
        found_first_hash = False
        while self.current_pos < len(self.source_code):
            char = self.advance()
            
            if char is None:
                break
            
            if char == '#':
                if found_first_hash:
                    # Found closing ##
                    return
                found_first_hash = True
            else:
                found_first_hash = False
        
        # If we reach here, comment was not closed
        self.errors.append({
            'type': 'Lexical Error',
            'message': f"Unclosed multi-line comment starting at line {start_line}, position {start_column}.",
            'line': start_line,
            'column': start_column
        })
    
    def read_string_literal(self):
        """Read a string literal enclosed in single quotes"""
        start_line = self.current_line
        start_column = self.current_column
        
        # Skip opening quote
        self.advance()
        
        value = ''
        while self.current_pos < len(self.source_code):
            char = self.peek()
            
            if char is None:
                self.errors.append({
                    'type': 'Lexical Error',
                    'message': f"Unclosed string literal starting at line {start_line}, position {start_column}.",
                    'line': start_line,
                    'column': start_column
                })
                return None
            
            if char == '\'':
                # Check for escaped quote
                if self.peek(1) == '\'':
                    value += '\''
                    self.advance()
                    self.advance()
                else:
                    # Closing quote
                    self.advance()
                    return Token('STRING_LITERAL', value, start_line, start_column)
            elif char == '\n':
                self.errors.append({
                    'type': 'Lexical Error',
                    'message': f"Unclosed string literal starting at line {start_line}, position {start_column}. Newline found before closing quote.",
                    'line': start_line,
                    'column': start_column
                })
                return None
            else:
                value += char
                self.advance()
        
        # EOF reached without closing quote
        self.errors.append({
            'type': 'Lexical Error',
            'message': f"Unclosed string literal starting at line {start_line}, position {start_column}.",
            'line': start_line,
            'column': start_column
        })
        return None
    
    def read_number(self):
        """Read a numeric literal (integer or float)"""
        start_line = self.current_line
        start_column = self.current_column
        
        value = ''
        has_dot = False
        
        while self.current_pos < len(self.source_code):
            char = self.peek()
            
            if char.isdigit():
                value += char
                self.advance()
            elif char == '.' and not has_dot:
                value += char
                has_dot = True
                self.advance()
                # Check if there's a digit after dot
                if self.peek() and not self.peek().isdigit():
                    self.errors.append({
                        'type': 'Lexical Error',
                        'message': f"Invalid number format at line {start_line}, position {start_column}. Expected digit after decimal point.",
                        'line': start_line,
                        'column': start_column
                    })
                    return None
            else:
                break
        
        if has_dot:
            return Token('FLOAT_LITERAL', value, start_line, start_column)
        else:
            return Token('INT_LITERAL', value, start_line, start_column)
    
    def read_identifier_or_keyword(self):
        """Read an identifier or keyword"""
        start_line = self.current_line
        start_column = self.current_column
        
        value = ''
        
        # First character must be a letter
        char = self.peek()
        if char and char.isalpha():
            value += char
            self.advance()
        else:
            return None
        
        # Subsequent characters can be letters, digits, or underscores
        while self.current_pos < len(self.source_code):
            char = self.peek()
            if char and (char.isalnum() or char == '_'):
                value += char
                self.advance()
            else:
                break
        
        # Check if it's a keyword
        if value in self.KEYWORDS:
            return Token('KEYWORD', value, start_line, start_column)
        else:
            return Token('IDENTIFIER', value, start_line, start_column)
    
    def read_operator(self):
        """Read an operator"""
        start_line = self.current_line
        start_column = self.current_column
        
        char = self.peek()
        if char is None:
            return None
        
        # Two-character operators
        two_char_ops = ['<=', '>=', '<>', '!=']
        if self.current_pos + 1 < len(self.source_code):
            two_char = char + self.source_code[self.current_pos + 1]
            if two_char in two_char_ops:
                self.advance()
                self.advance()
                return Token('OPERATOR', two_char, start_line, start_column)
        
        # Single-character operators
        if char in self.OPERATORS:
            self.advance()
            return Token('OPERATOR', char, start_line, start_column)
        
        return None
    
    def read_delimiter(self):
        """Read a delimiter"""
        start_line = self.current_line
        start_column = self.current_column
        
        char = self.peek()
        if char in self.DELIMITERS:
            self.advance()
            return Token('DELIMITER', char, start_line, start_column)
        
        return None
    
    def tokenize(self):
        """Main tokenization method"""
        self.tokens = []
        self.errors = []
        self.current_pos = 0
        self.current_line = 1
        self.current_column = 1
        
        while self.current_pos < len(self.source_code):
            # Skip whitespace
            self.skip_whitespace()
            
            if self.current_pos >= len(self.source_code):
                break
            
            char = self.peek()
            
            # Handle comments
            if char == '-' and self.peek(1) == '-':
                self.handle_single_line_comment()
                continue
            elif char == '#':
                if self.peek(1) == '#':
                    self.handle_multi_line_comment()
                    continue
            
            # Handle string literals
            if char == '\'':
                token = self.read_string_literal()
                if token:
                    self.tokens.append(token)
                continue
            
            # Handle numbers
            if char.isdigit():
                token = self.read_number()
                if token:
                    self.tokens.append(token)
                continue
            
            # Handle identifiers/keywords
            if char.isalpha():
                token = self.read_identifier_or_keyword()
                if token:
                    self.tokens.append(token)
                    continue
            
            # Handle operators
            token = self.read_operator()
            if token:
                self.tokens.append(token)
                continue
            
            # Handle delimiters
            token = self.read_delimiter()
            if token:
                self.tokens.append(token)
                continue
            
            # Invalid character
            self.errors.append({
                'type': 'Lexical Error',
                'message': f"Invalid character '{char}' at line {self.current_line}, position {self.current_column}.",
                'line': self.current_line,
                'column': self.current_column
            })
            self.advance()
        
        # Add EOF token
        self.tokens.append(Token('EOF', '', self.current_line, self.current_column))
        
        return self.tokens
    
    def get_tokens(self):
        """Get the list of tokens"""
        return self.tokens
    
    def get_errors(self):
        """Get the list of errors"""
        return self.errors
    
    def print_tokens(self):
        """Print all tokens in a formatted way"""
        print("=" * 60)
        print("LEXICAL ANALYSIS OUTPUT")
        print("=" * 60)
        
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  {error['type']}: {error['message']}")
            print()
        
        print("TOKENS:")
        for token in self.tokens:
            print(f"  {token}")
        
        print(f"\nTotal tokens: {len(self.tokens)}")
        print("=" * 60)

