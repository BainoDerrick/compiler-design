# lexer.py - UPDATED with specific error messages

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"


class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def current_char(self):
        if self.position < len(self.source):
            return self.source[self.position]
        return None
    
    def advance(self):
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def peek_next_char(self):
        if self.position + 1 < len(self.source):
            return self.source[self.position + 1]
        return None
    
    def add_token(self, type_, value=None):
        token = Token(type_, value, self.line, self.column)
        self.tokens.append(token)
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char().isspace():
            self.advance()
    
    def read_number(self):
        """Read integers AND floats"""
        num_str = ""
        is_float = False
        start_line = self.line
        start_col = self.column
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if is_float:
                    # Multiple decimal points - INVALID FLOAT
                    raise Exception(f"Invalid float number at line {start_line}, column {start_col}: too many decimal points")
                is_float = True
            num_str += self.current_char()
            self.advance()
        
        if is_float:
            # Check if it ends with a dot (invalid)
            if num_str.endswith('.'):
                raise Exception(f"Invalid float number at line {start_line}, column {start_col}: number cannot end with '.'")
            # Check if it starts with a dot (invalid)
            if num_str.startswith('.'):
                raise Exception(f"Invalid float number at line {start_line}, column {start_col}: number cannot start with '.'")
            self.add_token("FLOAT", float(num_str))
        else:
            self.add_token("NUMBER", int(num_str))
    
    def read_string(self):
        """Read string literals like "hello" """
        start_line = self.line
        start_col = self.column
        self.advance()  # skip opening "
        str_value = ""
        while self.current_char() and self.current_char() != '"':
            str_value += self.current_char()
            self.advance()
        
        if self.current_char() == '"':
            self.advance()  # skip closing "
            self.add_token("STRING", str_value)
        else:
            raise Exception(f"Unterminated string at line {start_line}, column {start_col}: missing closing '\"'")
    
    def read_character(self):
        """Read character literals like 'a' """
        start_line = self.line
        start_col = self.column
        self.advance()  # skip opening '
        char_value = ""
        if self.current_char():
            char_value = self.current_char()
            self.advance()
        
        if self.current_char() == "'":
            self.advance()  # skip closing '
            if len(char_value) == 0:
                raise Exception(f"Invalid character at line {start_line}, column {start_col}: empty character literal")
            self.add_token("CHAR", char_value)
        else:
            raise Exception(f"Unterminated character at line {start_line}, column {start_col}: missing closing '''")
    
    def read_identifier_or_keyword(self):
        id_str = ""
        while self.current_char() and (self.current_char().isalpha() or self.current_char().isdigit() or self.current_char() == '_'):
            id_str += self.current_char()
            self.advance()
        
        keywords = {
            "if": "IF", "else": "ELSE", "while": "WHILE",
            "return": "RETURN", "int": "TYPE_INT", "float": "TYPE_FLOAT",
            "string": "TYPE_STRING", "char": "TYPE_CHAR", "bool": "TYPE_BOOL",
            "true": "TRUE", "false": "FALSE", "print": "PRINT"
        }
        
        if id_str in keywords:
            self.add_token(keywords[id_str], id_str)
        else:
            self.add_token("IDENTIFIER", id_str)
    
    def read_operator_or_symbol(self):
        char = self.current_char()
        start_line = self.line
        start_col = self.column
        
        # Two-character operators
        if char == '=':
            if self.peek_next_char() == '=':
                self.advance()
                self.advance()
                self.add_token("EQUAL_EQUAL", "==")
            else:
                self.advance()
                self.add_token("ASSIGN", "=")
            return
        
        elif char == '!':
            if self.peek_next_char() == '=':
                self.advance()
                self.advance()
                self.add_token("NOT_EQUAL", "!=")
                return
            else:
                raise Exception(f"Invalid character '!' at line {start_line}, column {start_col}: expected '!='")
        
        elif char == '<':
            if self.peek_next_char() == '=':
                self.advance()
                self.advance()
                self.add_token("LESS_EQUAL", "<=")
            else:
                self.advance()
                self.add_token("LESS", "<")
            return
        
        elif char == '>':
            if self.peek_next_char() == '=':
                self.advance()
                self.advance()
                self.add_token("GREATER_EQUAL", ">=")
            else:
                self.advance()
                self.add_token("GREATER", ">")
            return
        
        # Power operator ^
        elif char == '^':
            self.advance()
            self.add_token("POWER", "^")
            return
        
        # Single-character operators and symbols
        operators_symbols = {
            '+': "PLUS", '-': "MINUS", '*': "MULTIPLY", '/': "DIVIDE",
            '(': "LPAREN", ')': "RPAREN", '{': "LBRACE", '}': "RBRACE",
            ';': "SEMICOLON", ',': "COMMA"
        }
        
        if char in operators_symbols:
            self.add_token(operators_symbols[char], char)
            self.advance()
        elif char == '"':
            self.read_string()
        elif char == "'":
            self.read_character()
        else:
            raise Exception(f"Unknown character '{char}' at line {start_line}, column {start_col}")
    
    def tokenize(self):
        while self.current_char():
            if self.current_char().isspace():
                self.skip_whitespace()
                continue
            if self.current_char().isdigit():
                self.read_number()
                continue
            if self.current_char().isalpha() or self.current_char() == '_':
                self.read_identifier_or_keyword()
                continue
            self.read_operator_or_symbol()
        
        self.add_token("EOF", None)
        return self.tokens