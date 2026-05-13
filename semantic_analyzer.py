# semantic_analyzer.py - FIXED TYPE CHECKING

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
        
        for k, info in self.symbols.items():
            if info.name == name and info.scope == self.current_scope:
                self.errors.append(f"Line {line}: Variable '{name}' already declared in {self.current_scope} scope")
                return False
        
        self.symbols[key] = SymbolInfo(name, var_type, line, self.current_scope)
        return True
    
    def lookup(self, name: str, line: int):
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
        print(f"{'Name':<12} {'Type':<10} {'Scope':<12} {'Init':<6} {'Used':<6}")
        print("-" * 50)
        for info in self.symbols.values():
            print(f"{info.name:<12} {info.type:<10} {info.scope:<12} {info.initialized:<6} {info.used:<6}")


class TypeChecker:
    @staticmethod
    def get_type(expr, sym_table, line):
        """Get type of an expression with proper type checking"""
        if isinstance(expr, Number):
            return "int"
        elif isinstance(expr, Float):
            return "float"
        elif isinstance(expr, String):
            return "string"
        elif isinstance(expr, Character):
            return "char"
        elif isinstance(expr, Identifier):
            return sym_table.get_type(expr.name)
        elif isinstance(expr, BinaryOp):
            left_type = TypeChecker.get_type(expr.left, sym_table, line)
            right_type = TypeChecker.get_type(expr.right, sym_table, line)
            
            if left_type is None or right_type is None:
                return None
            
            # Type checking for binary operations
            if left_type != right_type:
                sym_table.errors.append(f"Line {line}: Type mismatch: cannot {expr.op} {left_type} and {right_type}")
                return None
            
            # Check if operation is valid for the type
            if expr.op in ['+', '-', '*', '/']:
                if left_type not in ['int', 'float']:
                    sym_table.errors.append(f"Line {line}: Operator '{expr.op}' not supported for type {left_type}")
                    return None
            
            return left_type
        return None
    
    @staticmethod
    def check_assignment(var_type, expr_type, line, sym_table):
        """Check if assignment is type compatible"""
        # Type compatibility matrix
        compatible = {
            'int': ['int'],
            'float': ['int', 'float'],
            'string': ['string'],
            'char': ['char']
        }
        
        if expr_type not in compatible.get(var_type, []):
            sym_table.errors.append(f"Line {line}: Type mismatch: cannot assign {expr_type} to {var_type}")
            return False
        return True


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
                print(f"  Declaration: {stmt.name} : {stmt.type}")
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
        elif isinstance(expr, Float):
            return str(expr.value)
        elif isinstance(expr, String):
            return f'"{expr.value}"'
        elif isinstance(expr, Character):
            return f"'{expr.value}'"
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryOp):
            return f"({self._expr_str(expr.left)} {expr.op} {self._expr_str(expr.right)})"
        return "?"
    
    def _visit_declaration(self, node: Declaration):
        var_type = node.type if hasattr(node, 'type') else "int"
        if self.sym_table.declare(node.name, var_type, 0):
            print(f"  ✓ {node.name} : {var_type}")
    
    def _visit_assignment(self, node: Assignment):
        print(f"\n  → {node.name} = {self._expr_str(node.expr)}")
        
        # Check if variable exists
        var_info = self.sym_table.lookup(node.name, 0)
        if not var_info:
            return
        
        # Get expression type
        expr_type = TypeChecker.get_type(node.expr, self.sym_table, 0)
        if expr_type is None:
            return
        
        # Check type compatibility
        if not TypeChecker.check_assignment(var_info.type, expr_type, 0, self.sym_table):
            return
        
        # Mark as initialized
        self.sym_table.mark_initialized(node.name, 0)
        var_info.used = True
        print(f"    ✓ Type OK: {var_info.type} = {expr_type}")
    
    def _visit_print(self, node: Print):
        print(f"\n  → print({self._expr_str(node.expr)})")
        
        expr_type = TypeChecker.get_type(node.expr, self.sym_table, 0)
        if expr_type:
            print(f"    ✓ Type: {expr_type}")
        
        # Check initialization for identifiers
        if isinstance(node.expr, Identifier):
            self.sym_table.check_initialized(node.expr.name, 0)
            info = self.sym_table.lookup(node.expr.name, 0)
            if info:
                info.used = True