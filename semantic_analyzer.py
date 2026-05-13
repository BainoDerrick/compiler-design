# semantic_analyzer.py - COMPLETE SCOPE HANDLING

from ast_nodes import *
from typing import Dict, List, Optional


class SymbolInfo:
    def __init__(self, name: str, var_type: str, line: int, scope: str):
        self.name = name
        self.type = var_type
        self.line = line
        self.scope = scope
        self.initialized = False
        self.used = False
    
    def __repr__(self):
        return f"{self.name}: {self.type} (scope={self.scope})"


class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, SymbolInfo] = {}
        self.scope_stack = ["global"]
        self.current_scope = "global"
        self.scope_counter = 0
        self.errors = []
        self.warnings = []
    
    def enter_scope(self, scope_name: str = None):
        self.scope_counter += 1
        if scope_name is None:
            scope_name = f"block_{self.scope_counter}"
        self.scope_stack.append(scope_name)
        self.current_scope = scope_name
        print(f"  → Entering scope: {self.current_scope}")
    
    def exit_scope(self):
        if len(self.scope_stack) > 1:
            exited = self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
            print(f"  ← Exiting scope: {exited} (back to {self.current_scope})")
            return exited
        return None
    
    def get_current_scope(self):
        return self.current_scope
    
    def declare(self, name: str, var_type: str, line: int) -> bool:
        # Check if already declared in current scope
        for info in self.symbols.values():
            if info.name == name and info.scope == self.current_scope:
                self.errors.append(f"Line {line}: Variable '{name}' already declared in scope '{self.current_scope}'")
                return False
        
        key = f"{self.current_scope}:{name}"
        self.symbols[key] = SymbolInfo(name, var_type, line, self.current_scope)
        return True
    
    def lookup(self, name: str, line: int):
        # Search from innermost to outermost scope
        for scope in reversed(self.scope_stack):
            for info in self.symbols.values():
                if info.name == name and info.scope == scope:
                    return info
        
        self.errors.append(f"Line {line}: Variable '{name}' not declared in current scope")
        return None
    
    def lookup_in_current_scope(self, name: str):
        for info in self.symbols.values():
            if info.name == name and info.scope == self.current_scope:
                return info
        return None
    
    def mark_initialized(self, name: str, line: int):
        info = self.lookup(name, line)
        if info:
            info.initialized = True
    
    def check_initialized(self, name: str, line: int):
        info = self.lookup(name, line)
        if info and not info.initialized:
            self.warnings.append(f"Line {line}: Variable '{name}' may be uninitialized")
    
    def get_type(self, name: str, line: int = 0):
        info = self.lookup(name, line)
        return info.type if info else None
    
    def display(self):
        print("\n" + "="*70)
        print("SYMBOL TABLE")
        print("="*70)
        print(f"{'Name':<12} {'Type':<10} {'Scope':<20} {'Line':<6} {'Init':<6} {'Used':<6}")
        print("-" * 70)
        
        # Sort by scope depth for better readability
        sorted_symbols = sorted(self.symbols.values(), key=lambda x: (x.scope, x.line))
        for info in sorted_symbols:
            print(f"{info.name:<12} {info.type:<10} {info.scope:<20} {info.line:<6} {info.initialized:<6} {info.used:<6}")
        
        print(f"\n📊 Current Scope: {self.current_scope}")
        print(f"📚 Scope Stack: {' → '.join(self.scope_stack)}")


class TypeChecker:
    @staticmethod
    def get_type(expr, sym_table, line):
        if isinstance(expr, Number):
            return "int"
        elif isinstance(expr, Float):
            return "float"
        elif isinstance(expr, String):
            return "string"
        elif isinstance(expr, Character):
            return "char"
        elif isinstance(expr, Identifier):
            return sym_table.get_type(expr.name, line)
        elif isinstance(expr, BinaryOp):
            left_type = TypeChecker.get_type(expr.left, sym_table, line)
            right_type = TypeChecker.get_type(expr.right, sym_table, line)
            
            if left_type is None or right_type is None:
                return None
            
            # Handle POWER operator (^)
            if expr.op == "POWER":
                if left_type in ["int", "float"] and right_type in ["int", "float"]:
                    if left_type == "float" or right_type == "float":
                        return "float"
                    return "int"
                else:
                    sym_table.errors.append(f"Line {line}: POWER operator (^) only works with numbers, got {left_type} and {right_type}")
                    return None
            
            # Arithmetic operators
            elif expr.op in ["PLUS", "MINUS", "MULTIPLY", "DIVIDE", "+", "-", "*", "/"]:
                if left_type in ["int", "float"] and right_type in ["int", "float"]:
                    if expr.op in ["DIVIDE", "/"]:
                        return "float"
                    if left_type == "float" or right_type == "float":
                        return "float"
                    return "int"
                else:
                    sym_table.errors.append(f"Line {line}: Arithmetic operators only work with numbers, got {left_type} and {right_type}")
                    return None
            
            # Comparison operators
            elif expr.op in ["EQUAL_EQUAL", "NOT_EQUAL", "LESS", "LESS_EQUAL", "GREATER", "GREATER_EQUAL", "==", "!=", "<", "<=", ">", ">="]:
                if left_type == right_type:
                    return "bool"
                else:
                    sym_table.errors.append(f"Line {line}: Cannot compare {left_type} and {right_type}")
                    return None
            
            else:
                sym_table.errors.append(f"Line {line}: Unknown operator {expr.op}")
                return None
        return None
    
    @staticmethod
    def check_assignment(var_type: str, expr_type: str, line: int, sym_table: SymbolTable) -> bool:
        if var_type in ["int", "float"] and expr_type in ["int", "float"]:
            return True
        if var_type == expr_type:
            return True
        
        sym_table.errors.append(f"Line {line}: Type mismatch: cannot assign {expr_type} to {var_type}")
        return False


class SemanticAnalyzer:
    def __init__(self):
        self.sym_table = SymbolTable()
    
    def analyze(self, ast: Program):
        print("\n" + "="*60)
        print("SEMANTIC ANALYSIS")
        print("="*60)
        
        print("\n📥 INPUT: AST from Parser")
        print("-" * 40)
        self._print_ast(ast)
        
        print("\n📋 PROCESSING (with scope tracking)")
        print("-" * 40)
        self._visit(ast)
        
        self.sym_table.display()
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"  ✅ Declarations: {len(self.sym_table.symbols)}")
        print(f"  📚 Scopes entered: {len(self.sym_table.scope_stack)}")
        print(f"  ❌ Errors: {len(self.sym_table.errors)}")
        print(f"  ⚠️ Warnings: {len(self.sym_table.warnings)}")
        
        for err in self.sym_table.errors:
            print(f"  Error: {err}")
        for warn in self.sym_table.warnings:
            print(f"  Warning: {warn}")
        
        return self.sym_table
    
    def _print_ast(self, node, indent=0):
        indent_str = "  " * indent
        class_name = node.__class__.__name__
        
        if class_name == "Program":
            print(f"{indent_str}Program")
            for stmt in node.statements:
                self._print_ast(stmt, indent + 1)
        elif class_name == "Block":
            print(f"{indent_str}Block {{")
            for stmt in node.statements:
                self._print_ast(stmt, indent + 1)
            print(f"{indent_str}}}")
        elif class_name == "WhileLoop":
            print(f"{indent_str}WhileLoop")
            print(f"{indent_str}  condition: {self._expr_str(node.condition)}")
            print(f"{indent_str}  body:")
            self._print_ast(node.body, indent + 2)
        elif class_name == "ForLoop":
            print(f"{indent_str}ForLoop")
            if node.init:
                print(f"{indent_str}  init: {self._stmt_str(node.init)}")
            if node.condition:
                print(f"{indent_str}  condition: {self._expr_str(node.condition)}")
            if node.update:
                print(f"{indent_str}  update: {self._stmt_str(node.update)}")
            print(f"{indent_str}  body:")
            self._print_ast(node.body, indent + 2)
        elif class_name == "IfStatement":
            print(f"{indent_str}IfStatement")
            print(f"{indent_str}  condition: {self._expr_str(node.condition)}")
            print(f"{indent_str}  then:")
            self._print_ast(node.then_body, indent + 2)
            if node.else_body:
                print(f"{indent_str}  else:")
                self._print_ast(node.else_body, indent + 2)
        elif class_name == "Declaration":
            print(f"{indent_str}Declaration: {node.name} : {node.type}")
        elif class_name == "Assignment":
            print(f"{indent_str}Assignment: {node.name} = {self._expr_str(node.expr)}")
        elif class_name == "Print":
            print(f"{indent_str}Print: {self._expr_str(node.expr)}")
    
    def _expr_str(self, expr):
        if isinstance(expr, Number):
            return str(expr.value)
        elif isinstance(expr, Float):
            return str(expr.value)
        elif isinstance(expr, String):
            return f'"{expr.value}"'
        elif isinstance(expr, Character):
            return f"'{expr.value}'"
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryOp):
            op_str = expr.op
            if op_str == "POWER":
                op_str = "^"
            return f"({self._expr_str(expr.left)} {op_str} {self._expr_str(expr.right)})"
        return "?"
    
    def _stmt_str(self, stmt):
        if isinstance(stmt, Assignment):
            return f"{stmt.name} = {self._expr_str(stmt.expr)}"
        return str(stmt)
    
    def _visit(self, node):
        class_name = node.__class__.__name__
        
        if class_name == "Program":
            for stmt in node.statements:
                self._visit(stmt)
        
        elif class_name == "Block":
            self.sym_table.enter_scope("block")
            for stmt in node.statements:
                self._visit(stmt)
            self.sym_table.exit_scope()
        
        elif class_name == "WhileLoop":
            # Check condition
            cond_type = TypeChecker.get_type(node.condition, self.sym_table, 0)
            if cond_type and cond_type not in ["int", "float", "bool"]:
                self.sym_table.errors.append(f"While condition must be numeric or boolean, got {cond_type}")
            
            self.sym_table.enter_scope("while_loop")
            self._visit(node.body)
            self.sym_table.exit_scope()
        
        elif class_name == "ForLoop":
            self.sym_table.enter_scope("for_loop")
            
            if node.init:
                if isinstance(node.init, list):
                    for stmt in node.init:
                        self._visit(stmt)
                else:
                    self._visit(node.init)
            
            if node.condition:
                cond_type = TypeChecker.get_type(node.condition, self.sym_table, 0)
                if cond_type and cond_type not in ["int", "float", "bool"]:
                    self.sym_table.errors.append(f"For loop condition must be numeric or boolean, got {cond_type}")
            
            if node.update:
                self._visit(node.update)
            
            self._visit(node.body)
            self.sym_table.exit_scope()
        
        elif class_name == "IfStatement":
            cond_type = TypeChecker.get_type(node.condition, self.sym_table, 0)
            if cond_type and cond_type not in ["int", "float", "bool"]:
                self.sym_table.errors.append(f"If condition must be numeric or boolean, got {cond_type}")
            
            self.sym_table.enter_scope("if_then")
            self._visit(node.then_body)
            self.sym_table.exit_scope()
            
            if node.else_body:
                self.sym_table.enter_scope("if_else")
                self._visit(node.else_body)
                self.sym_table.exit_scope()
        
        elif class_name == "Declaration":
            self._visit_declaration(node)
        
        elif class_name == "Assignment":
            self._visit_assignment(node)
        
        elif class_name == "Print":
            self._visit_print(node)
    
    def _visit_declaration(self, node: Declaration):
        if self.sym_table.declare(node.name, node.type, 0):
            print(f"  ✓ Declared: {node.name} : {node.type} (scope: {self.sym_table.current_scope})")
    
    def _visit_assignment(self, node: Assignment):
        print(f"\n  → {node.name} = {self._expr_str(node.expr)} (scope: {self.sym_table.current_scope})")
        
        info = self.sym_table.lookup(node.name, 0)
        if not info:
            return
        
        expr_type = TypeChecker.get_type(node.expr, self.sym_table, 0)
        if expr_type:
            if TypeChecker.check_assignment(info.type, expr_type, 0, self.sym_table):
                self.sym_table.mark_initialized(node.name, 0)
                print(f"    ✓ Type: {expr_type} → {info.type}")
                info.used = True
    
    def _visit_print(self, node: Print):
        print(f"\n  → print({self._expr_str(node.expr)}) (scope: {self.sym_table.current_scope})")
        
        expr_type = TypeChecker.get_type(node.expr, self.sym_table, 0)
        if expr_type:
            print(f"    ✓ Type: {expr_type}")
        
        if isinstance(node.expr, Identifier):
            self.sym_table.check_initialized(node.expr.name, 0)
            info = self.sym_table.lookup(node.expr.name, 0)
            if info:
                info.used = True