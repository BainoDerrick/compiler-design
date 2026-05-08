# semantic_analyzer.py - PRACTICAL SEMANTIC ANALYZER
# Does: Symbol Table + Type Checking + Scope Management

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
        self.current_scope = "global"
        self.errors = []
        self.warnings = []
    
    def enter_scope(self, scope_name: str):
        self.current_scope = scope_name
    
    def exit_scope(self):
        self.current_scope = "global"
    
    def declare(self, name: str, var_type: str, line: int) -> bool:
        key = f"{self.current_scope}:{name}"
        
        # Check if already declared in current scope
        for k, info in self.symbols.items():
            if info.name == name and info.scope == self.current_scope:
                self.errors.append(f"Line {line}: Variable '{name}' already declared")
                return False
        
        self.symbols[key] = SymbolInfo(name, var_type, line, self.current_scope)
        return True
    
    def lookup(self, name: str, line: int):
        # Search current scope first, then global
        for info in self.symbols.values():
            if info.name == name:
                if info.scope == self.current_scope or info.scope == "global":
                    return info
        
        self.errors.append(f"Line {line}: Variable '{name}' not declared")
        return None
    
    def mark_initialized(self, name: str, line: int):
        info = self.lookup(name, line)
        if info:
            info.initialized = True
    
    def check_initialized(self, name: str, line: int):
        info = self.lookup(name, line)
        if info and not info.initialized:
            self.warnings.append(f"Line {line}: Variable '{name}' may be uninitialized")
    
    def get_type(self, name: str):
        info = self.lookup(name, 0)
        return info.type if info else None
    
    def display(self):
        print("\n" + "="*60)
        print("SYMBOL TABLE")
        print("="*60)
        print(f"{'Name':<12} {'Type':<8} {'Scope':<12} {'Init':<6} {'Used':<6}")
        print("-" * 50)
        for info in self.symbols.values():
            print(f"{info.name:<12} {info.type:<8} {info.scope:<12} {info.initialized:<6} {info.used:<6}")


class TypeChecker:
    @staticmethod
    def get_type(expr, sym_table, line):
        if isinstance(expr, Number):
            return "int"
        elif isinstance(expr, Identifier):
            return sym_table.get_type(expr.name)
        elif isinstance(expr, BinaryOp):
            left = TypeChecker.get_type(expr.left, sym_table, line)
            right = TypeChecker.get_type(expr.right, sym_table, line)
            if left and right and left == right:
                return left
            if left and right and left != right:
                sym_table.errors.append(f"Line {line}: Type mismatch: {left} {expr.op} {right}")
        return None


class SemanticAnalyzer:
    def __init__(self):
        self.sym_table = SymbolTable()
    
    def analyze(self, ast: Program):
        print("\n" + "="*60)
        print("SEMANTIC ANALYSIS")
        print("="*60)
        
        # Show input AST
        print("\n📥 INPUT: AST from Parser")
        print("-" * 40)
        for stmt in ast.statements:
            if isinstance(stmt, Declaration):
                print(f"  Declaration: {stmt.name}")
            elif isinstance(stmt, Assignment):
                print(f"  Assignment: {stmt.name} = {self._expr_str(stmt.expr)}")
            elif isinstance(stmt, Print):
                print(f"  Print: {self._expr_str(stmt.expr)}")
        
        # Process declarations
        print("\n📋 PROCESSING DECLARATIONS")
        print("-" * 40)
        for stmt in ast.statements:
            if isinstance(stmt, Declaration):
                self._visit_declaration(stmt)
        
        # Process statements
        print("\n🔍 PROCESSING STATEMENTS")
        print("-" * 40)
        for stmt in ast.statements:
            if isinstance(stmt, Assignment):
                self._visit_assignment(stmt)
            elif isinstance(stmt, Print):
                self._visit_print(stmt)
        
        # Display results
        self.sym_table.display()
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"  ✅ Declarations: {len(self.sym_table.symbols)}")
        print(f"  ❌ Errors: {len(self.sym_table.errors)}")
        print(f"  ⚠️ Warnings: {len(self.sym_table.warnings)}")
        
        for err in self.sym_table.errors:
            print(f"  Error: {err}")
        for warn in self.sym_table.warnings:
            print(f"  Warning: {warn}")
        
        return self.sym_table
    
    def _expr_str(self, expr):
        if isinstance(expr, Number):
            return str(expr.value)
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryOp):
            return f"({self._expr_str(expr.left)} {expr.op} {self._expr_str(expr.right)})"
        return "?"
    
    def _visit_declaration(self, node: Declaration):
        if self.sym_table.declare(node.name, "int", 0):
            print(f"  ✓ {node.name} : int")
    
    def _visit_assignment(self, node: Assignment):
        print(f"\n  → {node.name} = {self._expr_str(node.expr)}")
        
        # Check variable exists
        if not self.sym_table.lookup(node.name, 0):
            return
        
        # Type check
        expr_type = TypeChecker.get_type(node.expr, self.sym_table, 0)
        if expr_type:
            self.sym_table.mark_initialized(node.name, 0)
            print(f"    ✓ Type: {expr_type}")
    
    def _visit_print(self, node: Print):
        print(f"\n  → print({self._expr_str(node.expr)})")
        
        expr_type = TypeChecker.get_type(node.expr, self.sym_table, 0)
        if expr_type:
            print(f"    ✓ Type: {expr_type}")
        
        # Check initialization for identifiers
        if isinstance(node.expr, Identifier):
            self.sym_table.check_initialized(node.expr.name, 0)


# ============================================
# TEST FUNCTIONS
# ============================================

def test_valid_program():
    print("\n" + "█"*60)
    print("TEST 1: VALID PROGRAM")
    print("█"*60)
    
    ast = Program([
        Declaration('x'),
        Declaration('y'),
        Assignment('x', Number(5)),
        Assignment('y', BinaryOp(Identifier('x'), '+', Number(3))),
        Print(Identifier('y'))
    ])
    
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)


def test_undeclared_variable():
    print("\n" + "█"*60)
    print("TEST 2: UNDECLARED VARIABLE")
    print("█"*60)
    
    ast = Program([
        Declaration('x'),
        Assignment('y', Number(5)),  # y not declared
        Print(Identifier('y'))
    ])
    
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)


def test_uninitialized_variable():
    print("\n" + "█"*60)
    print("TEST 3: UNINITIALIZED VARIABLE")
    print("█"*60)
    
    ast = Program([
        Declaration('x'),
        Print(Identifier('x'))  # x not initialized
    ])
    
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)


def test_redeclaration():
    print("\n" + "█"*60)
    print("TEST 4: REDECLARATION")
    print("█"*60)
    
    ast = Program([
        Declaration('x'),
        Declaration('x'),  # x already declared
        Assignment('x', Number(5)),
        Print(Identifier('x'))
    ])
    
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)


if __name__ == "__main__":
    print("\n  Choose test:")
    print("  1. Valid Program")
    print("  2. Undeclared Variable Error")
    print("  3. Uninitialized Variable Warning")
    print("  4. Redeclaration Error")
    
    choice = input("\n  Enter choice (1-4): ")
    
    if choice == "1":
        test_valid_program()
    elif choice == "2":
        test_undeclared_variable()
    elif choice == "3":
        test_uninitialized_variable()
    elif choice == "4":
        test_redeclaration()
    else:
        test_valid_program()