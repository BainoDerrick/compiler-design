# parser.py - UPDATED with comparison operators

from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def eat(self, token_type):
        token = self.current_token()
        if token is None:
            last_token = self.tokens[-2] if len(self.tokens) > 1 else None
            if last_token:
                error_msg = f"Expected {token_type} at line {last_token.line}, column {last_token.column + 1}, but found END OF FILE"
            else:
                error_msg = f"Expected {token_type} at end of file"
            self.errors.append(error_msg)
            raise Exception(error_msg)
        
        if token.type == token_type:
            self.position += 1
        else:
            error_msg = f"Expected {token_type} at line {token.line}, column {token.column}, but got {token.type} ('{token.value}')"
            self.errors.append(error_msg)
            raise Exception(error_msg)

    def parse_program(self):
        try:
            statements = self.parse_statement_list()
            return Program(statements)
        except Exception as e:
            raise

    def parse_statement_list(self):
        statements = []
        while self.current_token() and self.current_token().type not in ("EOF", "RBRACE"):
            stmt = self.parse_statement()
            if isinstance(stmt, list):
                statements.extend(stmt)
            else:
                statements.append(stmt)
        return statements

    def parse_statement(self):
        token = self.current_token()
        
        if token.type in ("TYPE_INT", "TYPE_FLOAT", "TYPE_STRING", "TYPE_CHAR"):
            return self.parse_declaration()
        elif token.type == "IDENTIFIER":
            return self.parse_assignment()
        elif token.type == "PRINT":
            return self.parse_print()
        elif token.type == "WHILE":
            return self.parse_while()
        elif token.type == "FOR":
            return self.parse_for()
        elif token.type == "IF":
            return self.parse_if()
        elif token.type == "LBRACE":
            return self.parse_block()
        else:
            error_msg = f"Unexpected token {token.type} at line {token.line}, column {token.column}"
            self.errors.append(error_msg)
            raise Exception(error_msg)

    def parse_block(self):
        self.eat("LBRACE")
        statements = []
        while self.current_token() and self.current_token().type != "RBRACE":
            stmt = self.parse_statement()
            if isinstance(stmt, list):
                statements.extend(stmt)
            else:
                statements.append(stmt)
        self.eat("RBRACE")
        return Block(statements)

    def parse_declaration(self):
        token = self.current_token()
        var_type = token.value
        self.eat(token.type)
        name_token = self.current_token()
        name = name_token.value
        self.eat("IDENTIFIER")
        
        next_token = self.current_token()
        if next_token and next_token.type == "ASSIGN":
            self.eat("ASSIGN")
            init_value = self.parse_expression()
            
            semicolon_token = self.current_token()
            if semicolon_token is None or semicolon_token.type != "SEMICOLON":
                error_msg = f"Missing ';' after initialization of '{name}'"
                self.errors.append(error_msg)
                raise Exception(error_msg)
            
            self.eat("SEMICOLON")
            decl = Declaration(name, var_type)
            assign = Assignment(name, init_value)
            return [decl, assign]
        
        if next_token is None or next_token.type != "SEMICOLON":
            error_msg = f"Missing ';' after declaration of '{name}'"
            self.errors.append(error_msg)
            raise Exception(error_msg)
        
        self.eat("SEMICOLON")
        return Declaration(name, var_type)

    def parse_while(self):
        self.eat("WHILE")
        self.eat("LPAREN")
        condition = self.parse_expression()
        self.eat("RPAREN")
        
        if self.current_token() and self.current_token().type == "LBRACE":
            body = self.parse_block()
        else:
            body = self.parse_statement()
        
        return WhileLoop(condition, body)

    def parse_for(self):
        self.eat("FOR")
        self.eat("LPAREN")
        
        init = None
        if self.current_token().type != "SEMICOLON":
            init = self.parse_statement()
        self.eat("SEMICOLON")
        
        condition = None
        if self.current_token().type != "SEMICOLON":
            condition = self.parse_expression()
        self.eat("SEMICOLON")
        
        update = None
        if self.current_token().type != "RPAREN":
            update_token = self.current_token()
            if update_token.type == "IDENTIFIER":
                name = update_token.value
                self.eat("IDENTIFIER")
                self.eat("ASSIGN")
                expr = self.parse_expression()
                update = Assignment(name, expr)
        self.eat("RPAREN")
        
        if self.current_token() and self.current_token().type == "LBRACE":
            body = self.parse_block()
        else:
            body = self.parse_statement()
        
        return ForLoop(init, condition, update, body)

    def parse_if(self):
        self.eat("IF")
        self.eat("LPAREN")
        condition = self.parse_expression()
        self.eat("RPAREN")
        
        if self.current_token() and self.current_token().type == "LBRACE":
            then_body = self.parse_block()
        else:
            then_body = self.parse_statement()
        
        else_body = None
        if self.current_token() and self.current_token().type == "ELSE":
            self.eat("ELSE")
            if self.current_token() and self.current_token().type == "LBRACE":
                else_body = self.parse_block()
            else:
                else_body = self.parse_statement()
        
        return IfStatement(condition, then_body, else_body)

    def parse_assignment(self):
        token = self.current_token()
        name = token.value
        name_token = token
        self.eat("IDENTIFIER")
        self.eat("ASSIGN")
        expr = self.parse_expression()
        
        next_token = self.current_token()
        if next_token is None or next_token.type != "SEMICOLON":
            error_msg = f"Missing ';' after assignment to '{name}'"
            self.errors.append(error_msg)
            raise Exception(error_msg)
        
        self.eat("SEMICOLON")
        return Assignment(name, expr)

    def parse_print(self):
        start_line = self.current_token().line if self.current_token() else 0
        self.eat("PRINT")
        self.eat("LPAREN")
        expr = self.parse_expression()
        self.eat("RPAREN")
        
        next_token = self.current_token()
        if next_token is None or next_token.type != "SEMICOLON":
            error_msg = f"Missing ';' after print statement at line {start_line}"
            self.errors.append(error_msg)
            raise Exception(error_msg)
        
        self.eat("SEMICOLON")
        return Print(expr)

    def parse_expression(self):
        """Parse expressions with comparison operators"""
        node = self.parse_comparison()
        return node

    def parse_comparison(self):
        """Parse comparison operations (<, <=, >, >=, ==, !=)"""
        node = self.parse_arith_expr()
        
        while self.current_token() and self.current_token().type in ("LESS", "LESS_EQUAL", "GREATER", "GREATER_EQUAL", "EQUAL_EQUAL", "NOT_EQUAL"):
            op = self.current_token().type
            self.eat(op)
            right = self.parse_arith_expr()
            node = BinaryOp(node, op, right)
        
        return node

    def parse_arith_expr(self):
        """Parse arithmetic expressions (+, -)"""
        node = self.parse_term()
        
        while self.current_token() and self.current_token().type in ("PLUS", "MINUS"):
            op = self.current_token().type
            self.eat(op)
            right = self.parse_term()
            node = BinaryOp(node, op, right)
        
        return node

    def parse_term(self):
        """Parse term (*, /, ^)"""
        node = self.parse_factor()
        
        while self.current_token() and self.current_token().type in ("MULTIPLY", "DIVIDE", "POWER"):
            op = self.current_token().type
            self.eat(op)
            right = self.parse_factor()
            node = BinaryOp(node, op, right)
        
        return node

    def parse_factor(self):
        token = self.current_token()
        
        if token.type in ("NUMBER", "FLOAT", "STRING", "CHAR"):
            self.eat(token.type)
            if token.type == "NUMBER":
                return Number(token.value)
            elif token.type == "FLOAT":
                return Float(token.value)
            elif token.type == "STRING":
                return String(token.value)
            elif token.type == "CHAR":
                return Character(token.value)
        elif token.type == "IDENTIFIER":
            self.eat("IDENTIFIER")
            return Identifier(token.value)
        elif token.type == "LPAREN":
            self.eat("LPAREN")
            node = self.parse_expression()
            self.eat("RPAREN")
            return node
        else:
            error_msg = f"Unexpected token {token.type} at line {token.line}, column {token.column}"
            self.errors.append(error_msg)
            raise Exception(error_msg)