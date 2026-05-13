# ast_nodes.py - ADD Block, ForLoop, IfStatement

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Program({self.statements})"

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Block({self.statements})"

class Declaration(ASTNode):
    def __init__(self, name, var_type):
        self.name = name
        self.type = var_type
    def __repr__(self):
        return f"Declaration({self.name}, {self.type})"

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

class WhileLoop(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"WhileLoop({self.condition}, {self.body})"

class ForLoop(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
    def __repr__(self):
        return f"ForLoop({self.init}, {self.condition}, {self.update}, {self.body})"

class IfStatement(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body
    def __repr__(self):
        return f"IfStatement({self.condition}, {self.then_body}, {self.else_body})"

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

class Float(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Float({self.value})"

class String(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"String({self.value})"

class Character(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Character({self.value})"

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Identifier({self.name})"