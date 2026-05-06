#Top-Down, LL(1), Recursive Descent Parser

# parser.py

from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def eat(self, token_type):
        token = self.current_token()
        if token.type == token_type:
            self.position += 1
        else:
            raise Exception(f"Expected {token_type}, got {token.type}")

    # -------- PROGRAM --------
    def parse_program(self):
        statements = self.parse_statement_list()
        return Program(statements)

    # -------- STATEMENTS --------
    def parse_statement_list(self):
        statements = []

        while self.current_token().type not in ("EOF", "RBRACE"):
            statements.append(self.parse_statement())

        return statements

    def parse_statement(self):
        token = self.current_token()

        if token.type == "TYPE_INT":
            return self.parse_declaration()
        elif token.type == "IDENTIFIER":
            return self.parse_assignment()
        elif token.type == "PRINT":
            return self.parse_print()
        else:
            raise Exception(f"Unexpected token {token.type}")

    # -------- DECLARATION --------
    def parse_declaration(self):
        self.eat("TYPE_INT")
        name = self.current_token().value
        self.eat("IDENTIFIER")
        self.eat("SEMICOLON")
        return Declaration(name)

    # -------- ASSIGNMENT --------
    def parse_assignment(self):
        name = self.current_token().value
        self.eat("IDENTIFIER")
        self.eat("ASSIGN")
        expr = self.parse_expression()
        self.eat("SEMICOLON")
        return Assignment(name, expr)

    # -------- PRINT --------
    def parse_print(self):
        self.eat("PRINT")
        self.eat("LPAREN")
        expr = self.parse_expression()
        self.eat("RPAREN")
        self.eat("SEMICOLON")
        return Print(expr)

    # -------- EXPRESSIONS --------
    def parse_expression(self):
        node = self.parse_term()

        while self.current_token().type in ("PLUS", "MINUS"):
            op = self.current_token().type
            self.eat(op)
            right = self.parse_term()
            node = BinaryOp(node, op, right)

        return node

    def parse_term(self):
        node = self.parse_factor()

        while self.current_token().type in ("MULTIPLY", "DIVIDE"):
            op = self.current_token().type
            self.eat(op)
            right = self.parse_factor()
            node = BinaryOp(node, op, right)

        return node

    def parse_factor(self):
        token = self.current_token()

        if token.type == "NUMBER":
            self.eat("NUMBER")
            return Number(token.value)

        elif token.type == "IDENTIFIER":
            self.eat("IDENTIFIER")
            return Identifier(token.value)

        elif token.type == "LPAREN":
            self.eat("LPAREN")
            node = self.parse_expression()
            self.eat("RPAREN")
            return node

        else:
            raise Exception(f"Unexpected token {token.type}")