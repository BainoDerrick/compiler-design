# defines the structure of the program (AST).

class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


class Declaration(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Declaration({self.name})"


class Assignment(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def __repr__(self):
        return f"Assignment({self.name}, {self.expr})"


class Print(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"


class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op}, {self.right})"


class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"


class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"