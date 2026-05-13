# main.py - COMPLETE COMPILER WITH BEAUTIFUL AST

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from lexer import Lexer
from parser import Parser
from syntax_analysis_bottom_up import LR0Parser, Grammar
from semantic_analyzer import SemanticAnalyzer
from IR_generator import (
    ThreeAddressCode, Optimizer, CodeGenerator,
    part1_ir_levels, part2_ir_structures, part3_tac, part4_complete_example
)
from ast_nodes import *


# ============================================
# GLOBAL VARIABLES
# ============================================

source_code = ""
tokens = []
ast = None
symbol_table = None


# ============================================
# COMPILER ENGINE
# ============================================

class CompilerEngine:
    def __init__(self):
        self.source_code = ""
        self.tokens = []
        self.ast = None
        self.symbol_table = None
        self.tac = None
        self.optimized_tac = None
        self.parse_tree_lines = []
        self.shift_reduce_trace = []
        self.errors = []
        self.stopped_at = None
    
    def compile(self, source_code):
        self.source_code = source_code
        self.errors = []
        self.stopped_at = None
        self.shift_reduce_trace = []
        
        try:
            lexer = Lexer(source_code)
            self.tokens = lexer.tokenize()
        except Exception as e:
            self.errors.append(f"LEXER ERROR: {str(e)}")
            self.stopped_at = "Lexer"
            return False
        
        try:
            parser = Parser(self.tokens)
            self.ast = parser.parse_program()
            self._build_parse_tree()
            self._build_shift_reduce_trace()
        except Exception as e:
            self.errors.append(f"PARSER ERROR: {str(e)}")
            self.stopped_at = "Parser"
            return False
        
        try:
            analyzer = SemanticAnalyzer()
            self.symbol_table = analyzer.analyze(self.ast)
            if self.symbol_table.errors:
                self.errors.extend(self.symbol_table.errors)
                self.stopped_at = "Semantic Analyzer"
                return False
        except Exception as e:
            self.errors.append(f"SEMANTIC ERROR: {str(e)}")
            self.stopped_at = "Semantic Analyzer"
            return False
        
        try:
            self.tac = ThreeAddressCode()
            self.tac.generate_from_ast(self.ast)
            self.optimized_tac = Optimizer.constant_folding(self.tac)
        except Exception as e:
            self.errors.append(f"IR ERROR: {str(e)}")
            self.stopped_at = "IR Generator"
            return False
        
        return True
    
    def _build_parse_tree(self):
        self.parse_tree_lines = ["Program", "│"]
        i = 0
        stmt_num = 1
        
        while i < len(self.tokens):
            token = self.tokens[i]
            
            if token.type in ("TYPE_INT", "TYPE_FLOAT", "TYPE_STRING", "TYPE_CHAR"):
                var_type = token.value
                self.parse_tree_lines.append(f"├── Statement {stmt_num}: Declaration")
                self.parse_tree_lines.append(f"│   ├── {var_type.upper()}: '{token.value}'")
                i += 1
                if i < len(self.tokens) and self.tokens[i].type == "IDENTIFIER":
                    self.parse_tree_lines.append(f"│   ├── IDENTIFIER: '{self.tokens[i].value}'")
                    i += 1
                if i < len(self.tokens) and self.tokens[i].type == "SEMICOLON":
                    self.parse_tree_lines.append(f"│   └── SEMICOLON: ';'")
                    i += 1
                stmt_num += 1
            elif token.type == "IDENTIFIER":
                var_name = token.value
                self.parse_tree_lines.append(f"├── Statement {stmt_num}: Assignment")
                self.parse_tree_lines.append(f"│   ├── IDENTIFIER: '{var_name}'")
                i += 1
                if i < len(self.tokens) and self.tokens[i].type == "ASSIGN":
                    self.parse_tree_lines.append(f"│   ├── ASSIGN: '='")
                    i += 1
                self.parse_tree_lines.append(f"│   ├── Expression")
                self.parse_tree_lines.append(f"│   │   └── Term")
                self.parse_tree_lines.append(f"│   │       └── Factor")
                if i < len(self.tokens) and self.tokens[i].type == "NUMBER":
                    self.parse_tree_lines.append(f"│   │           └── NUMBER: '{self.tokens[i].value}'")
                    i += 1
                elif i < len(self.tokens) and self.tokens[i].type == "IDENTIFIER":
                    self.parse_tree_lines.append(f"│   │           └── IDENTIFIER: '{self.tokens[i].value}'")
                    i += 1
                if i < len(self.tokens) and self.tokens[i].type == "SEMICOLON":
                    self.parse_tree_lines.append(f"│   └── SEMICOLON: ';'")
                    i += 1
                stmt_num += 1
            elif token.type == "PRINT":
                self.parse_tree_lines.append(f"├── Statement {stmt_num}: Print")
                self.parse_tree_lines.append(f"│   ├── PRINT: 'print'")
                i += 1
                if i < len(self.tokens) and self.tokens[i].type == "LPAREN":
                    self.parse_tree_lines.append(f"│   ├── LPAREN: '('")
                    i += 1
                self.parse_tree_lines.append(f"│   ├── Expression")
                self.parse_tree_lines.append(f"│   │   └── Term")
                self.parse_tree_lines.append(f"│   │       └── Factor")
                if i < len(self.tokens) and self.tokens[i].type == "IDENTIFIER":
                    self.parse_tree_lines.append(f"│   │           └── IDENTIFIER: '{self.tokens[i].value}'")
                    i += 1
                if i < len(self.tokens) and self.tokens[i].type == "RPAREN":
                    self.parse_tree_lines.append(f"│   ├── RPAREN: ')'")
                    i += 1
                if i < len(self.tokens) and self.tokens[i].type == "SEMICOLON":
                    self.parse_tree_lines.append(f"│   └── SEMICOLON: ';'")
                    i += 1
                stmt_num += 1
            else:
                i += 1
    
    def _build_shift_reduce_trace(self):
        self.shift_reduce_trace = []
        self.shift_reduce_trace.append("┌─────┬────────────────────────────────────────────────┬────────────────────────────────────────────────┬──────────────────────────────────────┐")
        self.shift_reduce_trace.append("│Step │ Stack                                          │ Remaining Input                               │ Action                               │")
        self.shift_reduce_trace.append("├─────┼────────────────────────────────────────────────┼────────────────────────────────────────────────┼──────────────────────────────────────┤")
        
        stream = []
        original_tokens = []
        for t in self.tokens:
            if t.type == "IDENTIFIER":
                stream.append("id")
                original_tokens.append(t.value)
            elif t.type == "NUMBER":
                stream.append("num")
                original_tokens.append(str(t.value))
            elif t.type == "TYPE_INT":
                stream.append("int")
                original_tokens.append("int")
            elif t.type == "ASSIGN":
                stream.append("=")
                original_tokens.append("=")
            elif t.type == "PRINT":
                stream.append("print")
                original_tokens.append("print")
            elif t.type == "LPAREN":
                stream.append("(")
                original_tokens.append("(")
            elif t.type == "RPAREN":
                stream.append(")")
                original_tokens.append(")")
            elif t.type == "SEMICOLON":
                stream.append(";")
                original_tokens.append(";")
        
        rules = [
            ("num", "E"), ("id", "E"),
            ("int id ;", "D"), ("id = E ;", "S"), ("print ( E ) ;", "P"),
            ("D", "StmtList"), ("S", "StmtList"), ("P", "StmtList"),
            ("StmtList StmtList", "StmtList"), ("StmtList", "Program")
        ]
        
        stack = []
        remaining = stream.copy()
        orig_remaining = original_tokens.copy()
        step = 1
        value_stack = []
        
        while remaining or len(stack) > 1:
            stack_str = ' '.join(stack) if stack else "empty"
            stack_str = stack_str[:46] + ".." if len(stack_str) > 46 else stack_str
            remain_str = ' '.join(remaining) if remaining else "empty"
            remain_str = remain_str[:46] + ".." if len(remain_str) > 46 else remain_str
            
            reduced = False
            current = ' '.join(stack)
            
            for pattern, result in rules:
                if current.endswith(pattern):
                    pattern_len = len(pattern.split())
                    reduced_vals = value_stack[-pattern_len:] if value_stack else []
                    for _ in range(pattern_len):
                        if stack: stack.pop()
                        if value_stack: value_stack.pop()
                    stack.append(result)
                    value_stack.append(result)
                    
                    if pattern == "num":
                        self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ REDUCE: {reduced_vals[0]} → {result}                              │")
                    elif pattern == "id":
                        self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ REDUCE: {reduced_vals[0]} → {result}                              │")
                    elif pattern == "int id ;":
                        self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ REDUCE: int {reduced_vals[1]} ; → {result}                       │")
                    elif pattern == "id = E ;":
                        self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ REDUCE: {reduced_vals[0]} = {reduced_vals[2]} ; → {result}        │")
                    elif pattern == "print ( E ) ;":
                        self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ REDUCE: print ( {reduced_vals[2]} ) ; → {result}                 │")
                    elif pattern == "StmtList" and result == "Program":
                        self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ REDUCE: StmtList → {result}                                      │")
                    else:
                        self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ REDUCE: {pattern} → {result}                                      │")
                    
                    step += 1
                    reduced = True
                    break
            
            if not reduced and remaining:
                next_tok = remaining.pop(0)
                next_val = orig_remaining.pop(0) if orig_remaining else next_tok
                stack.append(next_tok)
                value_stack.append(next_val)
                self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ SHIFT: {next_tok} ({next_val})                          │")
                step += 1
            
            if not remaining and len(stack) == 1 and stack[0] == "Program":
                self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ ACCEPT! ✓                                         │")
                break
            
            if not reduced and not remaining:
                if len(stack) == 1 and stack[0] == "Program":
                    self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ ACCEPT! ✓                                         │")
                else:
                    self.shift_reduce_trace.append(f"│{step:<4} │ {stack_str:<46} │ {remain_str:<46} │ Complete                                         │")
                break
        
        self.shift_reduce_trace.append("└─────┴────────────────────────────────────────────────┴────────────────────────────────────────────────┴──────────────────────────────────────┘")
    
    def get_beautiful_ast(self):
        output = []
        output.append("")
        output.append("        ╔═════════════╗")
        output.append("        ║   Program   ║")
        output.append("        ╚═════╤═══════╝")
        output.append("              │")
        
        first = True
        for stmt in self.ast.statements:
            if not first:
                output.append("              │")
            first = False
            if isinstance(stmt, Assignment):
                output.append(f"              ╔══════════╗")
                output.append(f"              ║    =     ║")
                output.append(f"              ╚═════╤════╝")
                output.append(f"                    │")
                output.append(f"                 ╔══╧══╗")
                output.append(f"                 ║ {stmt.name} ║")
                output.append(f"                 ╚══╤══╝")
                output.append(f"                    │")
                self._add_expr_ast(stmt.expr, output, "                    ")
            elif isinstance(stmt, Print):
                output.append(f"              ╔══════════╗")
                output.append(f"              ║   print  ║")
                output.append(f"              ╚═════╤════╝")
                output.append(f"                    │")
                self._add_expr_ast(stmt.expr, output, "                    ")
        
        return '\n'.join(output)
    
    def _add_expr_ast(self, expr, output, prefix):
        if isinstance(expr, Number):
            output.append(f"{prefix}╔══════╗")
            output.append(f"{prefix}║  {expr.value}  ║")
            output.append(f"{prefix}╚══════╝")
        elif isinstance(expr, Identifier):
            output.append(f"{prefix}╔══════╗")
            output.append(f"{prefix}║  {expr.name}  ║")
            output.append(f"{prefix}╚══════╝")
        elif isinstance(expr, BinaryOp):
            output.append(f"{prefix}╔══════╗")
            output.append(f"{prefix}║  {expr.op}  ║")
            output.append(f"{prefix}╚══╤═══╝")
            output.append(f"{prefix}   │")
            output.append(f"{prefix} ┌─┴─┐")
            output.append(f"{prefix}┌┴┐ ┌┴┐")
            self._add_expr_ast(expr.left, output, prefix + "│ ")
            self._add_expr_ast(expr.right, output, prefix + "  ")


# ============================================
# TEAM FUNCTIONS
# ============================================

def team1_lexer(engine, output_text):
    output_text.insert(tk.END, "█" * 80 + "\n")
    output_text.insert(tk.END, "█ TEAM 1: LEXICAL ANALYZER\n")
    output_text.insert(tk.END, "█" * 80 + "\n\n")
    
    output_text.insert(tk.END, "📄 YOUR SOURCE CODE:\n")
    output_text.insert(tk.END, "-" * 40 + "\n")
    output_text.insert(tk.END, engine.source_code + "\n\n")
    
    output_text.insert(tk.END, "🔤 TOKEN STREAM:\n")
    output_text.insert(tk.END, "-" * 60 + "\n")
    output_text.insert(tk.END, f"{'Index':<6} {'Type':<18} {'Value':<15} {'Line'}\n")
    output_text.insert(tk.END, "-" * 60 + "\n")
    
    for i, token in enumerate(engine.tokens):
        if token.type != "EOF":
            output_text.insert(tk.END, f"{i:<6} {token.type:<18} '{token.value}'{' '*(15-len(str(token.value))-2)} {token.line}\n")
    
    output_text.insert(tk.END, f"\n✅ Total tokens: {len(engine.tokens)}\n")


def team2_topdown_parser(engine, output_text):
    output_text.insert(tk.END, "█" * 80 + "\n")
    output_text.insert(tk.END, "█ TEAM 2: TOP-DOWN PARSER (LL(1))\n")
    output_text.insert(tk.END, "█" * 80 + "\n\n")
    
    output_text.insert(tk.END, "🌳 PARSE TREE:\n")
    output_text.insert(tk.END, "-" * 40 + "\n")
    for line in engine.parse_tree_lines:
        output_text.insert(tk.END, line + "\n")
    
    output_text.insert(tk.END, "\n🌳 ABSTRACT SYNTAX TREE (AST) - Operators & Operands Only:\n")
    output_text.insert(tk.END, "-" * 40 + "\n")
    output_text.insert(tk.END, engine.get_beautiful_ast() + "\n")


def team3_bottomup_parser(engine, output_text):
    output_text.insert(tk.END, "█" * 80 + "\n")
    output_text.insert(tk.END, "█ TEAM 3: BOTTOM-UP PARSER (LR(0) - Shift Reduce)\n")
    output_text.insert(tk.END, "█" * 80 + "\n\n")
    
    output_text.insert(tk.END, "📥 YOUR SOURCE CODE:\n")
    output_text.insert(tk.END, engine.source_code + "\n\n")
    
    stream = []
    for t in engine.tokens:
        if t.type == "IDENTIFIER":
            stream.append("id")
        elif t.type == "NUMBER":
            stream.append("num")
        elif t.type == "TYPE_INT":
            stream.append("int")
        elif t.type == "ASSIGN":
            stream.append("=")
        elif t.type == "PRINT":
            stream.append("print")
        elif t.type == "LPAREN":
            stream.append("(")
        elif t.type == "RPAREN":
            stream.append(")")
        elif t.type == "SEMICOLON":
            stream.append(";")
    
    output_text.insert(tk.END, "📜 Token Stream: " + ' '.join(stream) + "\n\n")
    
    output_text.insert(tk.END, "🔄 SHIFT-REDUCE EXPLANATION:\n\n")
    output_text.insert(tk.END, "    Bottom-Up parsing builds the PARSE TREE from LEAVES to ROOT.\n\n")
    output_text.insert(tk.END, "    SHIFT: Move token from input to stack\n")
    output_text.insert(tk.END, "    REDUCE: Replace symbols on stack with non-terminal\n\n")
    
    output_text.insert(tk.END, "📊 SHIFT-REDUCE TRACE:\n\n")
    for line in engine.shift_reduce_trace:
        output_text.insert(tk.END, line + "\n")


def team4_semantic(engine, output_text):
    output_text.insert(tk.END, "█" * 80 + "\n")
    output_text.insert(tk.END, "█ TEAM 4: SEMANTIC ANALYZER\n")
    output_text.insert(tk.END, "█" * 80 + "\n\n")
    
    output_text.insert(tk.END, "📋 SYMBOL TABLE:\n")
    output_text.insert(tk.END, "-" * 50 + "\n")
    output_text.insert(tk.END, f"{'Name':<12} {'Type':<10} {'Initialized':<12} {'Used':<6}\n")
    output_text.insert(tk.END, "-" * 50 + "\n")
    
    if engine.symbol_table:
        for info in engine.symbol_table.symbols.values():
            output_text.insert(tk.END, f"{info.name:<12} {info.type:<10} {str(info.initialized):<12} {info.used:<6}\n")
    
    output_text.insert(tk.END, f"\n✅ Variables declared: {len(engine.symbol_table.symbols) if engine.symbol_table else 0}\n")


def team5_ir_generator(engine, output_text):
    output_text.insert(tk.END, "█" * 80 + "\n")
    output_text.insert(tk.END, "█ TEAM 5: IR GENERATOR\n")
    output_text.insert(tk.END, "█" * 80 + "\n\n")
    
    output_text.insert(tk.END, "🔧 THREE-ADDRESS CODE (TAC):\n")
    output_text.insert(tk.END, "-" * 40 + "\n")
    output_text.insert(tk.END, f"{'Index':<6} {'Instruction'}\n")
    output_text.insert(tk.END, "-" * 40 + "\n")
    for i, instr in enumerate(engine.tac.instructions):
        output_text.insert(tk.END, f"{i:<6} {instr}\n")
    
    output_text.insert(tk.END, "\n⚡ OPTIMIZED TAC (Constant Folding):\n")
    output_text.insert(tk.END, "-" * 40 + "\n")
    for i, instr in enumerate(engine.optimized_tac.instructions):
        output_text.insert(tk.END, f"{i:<6} {instr}\n")
    
    output_text.insert(tk.END, "\n🎯 TARGET CODE:\n")
    output_text.insert(tk.END, "-" * 40 + "\n")
    output_text.insert(tk.END, "\n🐍 PYTHON CODE:\n")
    output_text.insert(tk.END, CodeGenerator.to_python(engine.optimized_tac) + "\n")
    output_text.insert(tk.END, "\n🔧 C CODE:\n")
    output_text.insert(tk.END, CodeGenerator.to_c(engine.optimized_tac) + "\n")


def ir_theory_only(output_text):
    output_text.insert(tk.END, "█" * 80 + "\n")
    output_text.insert(tk.END, "█ IR THEORY - Fixed Concepts\n")
    output_text.insert(tk.END, "█" * 80 + "\n\n")
    
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    part1_ir_levels()
    part2_ir_structures()
    part3_tac()
    part4_complete_example()
    theory_output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    output_text.insert(tk.END, theory_output)


# ============================================
# GUI APPLICATION
# ============================================

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compiler Project 2026")
        self.root.geometry("1400x850")
        self.root.configure(bg='#1e1e1e')
        
        self.engine = CompilerEngine()
        self.setup_ui()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="COMPILER PROJECT 2026", 
                         font=("Arial", 18, "bold"), bg='#1e1e1e', fg='#61dafb')
        title.pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # LEFT: Menu and Source Code
        left_frame = tk.Frame(main_frame, bg='#2d2d2d', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(left_frame, text="🎯 MAIN MENU", font=("Arial", 14, "bold"),
                 bg='#2d2d2d', fg='#61dafb').pack(pady=10)
        
        menu_frame = tk.Frame(left_frame, bg='#2d2d2d')
        menu_frame.pack(pady=10)
        
        buttons = [
            ("1. 📝 Team 1 - Lexical Analyzer", self.run_team1),
            ("2. 📚 Team 2 - Top-Down Parser", self.run_team2),
            ("3. 🔄 Team 3 - Bottom-Up Parser", self.run_team3),
            ("4. 🔍 Team 4 - Semantic Analyzer", self.run_team4),
            ("5. ⚡ Team 5 - IR Generator", self.run_team5),
            
            ("7. ❌ Exit", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = tk.Button(menu_frame, text=text, command=command,
                           bg='#3c3c3c', fg='white', font=("Arial", 10),
                           width=32, anchor='w', padx=10)
            btn.pack(pady=3)
        
        # Source code area
        tk.Label(left_frame, text="📝 ENTER YOUR SOURCE CODE", font=("Arial", 10, "bold"),
                 bg='#2d2d2d', fg='#61dafb').pack(pady=(20,5))
        
        self.source_text = scrolledtext.ScrolledText(left_frame, height=20, width=45,
                                                      font=("Consolas", 10),
                                                      bg='#1e1e1e', fg='#d4d4d4',
                                                      insertbackground='white')
        self.source_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # RIGHT: Output
        right_frame = tk.Frame(main_frame, bg='#1e1e1e')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.output_text = scrolledtext.ScrolledText(right_frame, font=("Consolas", 10),
                                                      bg='#1e1e1e', fg='#d4d4d4',
                                                      wrap=tk.NONE)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready - Enter code and select a team option",
                                      bg='#1e1e1e', fg='#61dafb', font=("Arial", 9))
        self.status_label.pack(pady=5)
    
    def get_source(self):
        return self.source_text.get(1.0, tk.END).strip()
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
    
    def run_team1(self):
        source = self.get_source()
        if not source:
            messagebox.showwarning("Warning", "Please enter source code first!")
            return
        
        self.clear_output()
        self.status_label.config(text="Running Team 1 - Lexer...")
        self.root.update()
        
        success = self.engine.compile(source)
        
        if success:
            team1_lexer(self.engine, self.output_text)
            self.status_label.config(text="✅ Team 1 - Lexer completed")
        else:
            if self.engine.stopped_at == "Lexer":
                self.output_text.insert(tk.END, "❌ LEXER FAILED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            else:
                team1_lexer(self.engine, self.output_text)
            self.status_label.config(text="❌ Lexer failed")
    
    def run_team2(self):
        source = self.get_source()
        if not source:
            messagebox.showwarning("Warning", "Please enter source code first!")
            return
        
        self.clear_output()
        self.status_label.config(text="Running Team 2 - Parser...")
        self.root.update()
        
        success = self.engine.compile(source)
        
        if not success:
            if self.engine.stopped_at == "Lexer":
                self.output_text.insert(tk.END, "❌ CANNOT RUN PARSER - LEXER FAILED FIRST!\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "LEXER ERRORS:\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            elif self.engine.stopped_at == "Parser":
                self.output_text.insert(tk.END, "❌ PARSER FAILED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            elif self.engine.stopped_at == "Semantic Analyzer":
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "LEXER OUTPUT (Tokens):\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n\n")
                team1_lexer(self.engine, self.output_text)
                self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
                
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "PARSER OUTPUT (Parse Tree & AST):\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n\n")
                team2_topdown_parser(self.engine, self.output_text)
                self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
                
                self.output_text.insert(tk.END, "❌ SEMANTIC ANALYSIS FAILED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            else:
                self.output_text.insert(tk.END, "❌ COMPILATION FAILED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            self.status_label.config(text="❌ Compilation failed")
            return
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "LEXER OUTPUT (Tokens):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team1_lexer(self.engine, self.output_text)
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "PARSER OUTPUT (Parse Tree & AST):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team2_topdown_parser(self.engine, self.output_text)
        
        self.status_label.config(text="✅ Team 2 - Parser completed")
    
    def run_team3(self):
        source = self.get_source()
        if not source:
            messagebox.showwarning("Warning", "Please enter source code first!")
            return
        
        self.clear_output()
        self.status_label.config(text="Running Team 3 - Bottom-Up Parser...")
        self.root.update()
        
        success = self.engine.compile(source)
        
        if not success:
            if self.engine.stopped_at == "Lexer":
                self.output_text.insert(tk.END, "❌ CANNOT RUN BOTTOM-UP PARSER - LEXER FAILED FIRST!\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "LEXER ERRORS:\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            elif self.engine.stopped_at == "Parser":
                self.output_text.insert(tk.END, "❌ BOTTOM-UP PARSER WOULD ALSO FAIL - TOP-DOWN PARSER FAILED FIRST!\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "PARSER ERRORS:\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            elif self.engine.stopped_at == "Semantic Analyzer":
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "LEXER OUTPUT (Tokens):\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n\n")
                team1_lexer(self.engine, self.output_text)
                self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
                
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "BOTTOM-UP PARSER (LR(0) - Shift Reduce):\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n\n")
                team3_bottomup_parser(self.engine, self.output_text)
                self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
                
                self.output_text.insert(tk.END, "⚠️ SEMANTIC ERROR DETECTED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            else:
                self.output_text.insert(tk.END, "❌ COMPILATION FAILED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            self.status_label.config(text="❌ Compilation failed")
            return
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "LEXER OUTPUT (Tokens):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team1_lexer(self.engine, self.output_text)
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "BOTTOM-UP PARSER (LR(0) - Shift Reduce):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team3_bottomup_parser(self.engine, self.output_text)
        
        self.status_label.config(text="✅ Team 3 - Bottom-Up Parser completed")
    
    def run_team4(self):
        source = self.get_source()
        if not source:
            messagebox.showwarning("Warning", "Please enter source code first!")
            return
        
        self.clear_output()
        self.status_label.config(text="Running Team 4 - Semantic Analyzer...")
        self.root.update()
        
        success = self.engine.compile(source)
        
        if not success:
            if self.engine.stopped_at == "Lexer":
                self.output_text.insert(tk.END, "❌ CANNOT RUN SEMANTIC ANALYZER - LEXER FAILED FIRST!\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "LEXER ERRORS:\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            elif self.engine.stopped_at == "Parser":
                self.output_text.insert(tk.END, "❌ CANNOT RUN SEMANTIC ANALYZER - PARSER FAILED FIRST!\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "PARSER ERRORS:\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            elif self.engine.stopped_at == "Semantic Analyzer":
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "LEXER OUTPUT (Tokens):\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n\n")
                team1_lexer(self.engine, self.output_text)
                self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
                
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "PARSER OUTPUT (AST):\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n\n")
                team2_topdown_parser(self.engine, self.output_text)
                self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
                
                self.output_text.insert(tk.END, "❌ SEMANTIC ANALYSIS FAILED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            else:
                self.output_text.insert(tk.END, "❌ COMPILATION FAILED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            self.status_label.config(text="❌ Compilation failed")
            return
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "LEXER OUTPUT (Tokens):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team1_lexer(self.engine, self.output_text)
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "PARSER OUTPUT (AST):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team2_topdown_parser(self.engine, self.output_text)
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "SEMANTIC OUTPUT (Symbol Table):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team4_semantic(self.engine, self.output_text)
        
        self.status_label.config(text="✅ Team 4 - Semantic Analyzer completed")
    
    def run_team5(self):
        source = self.get_source()
        if not source:
            messagebox.showwarning("Warning", "Please enter source code first!")
            return
        
        self.clear_output()
        self.status_label.config(text="Running Team 5 - IR Generator...")
        self.root.update()
        
        success = self.engine.compile(source)
        
        if not success:
            if self.engine.stopped_at == "Lexer":
                self.output_text.insert(tk.END, "❌ CANNOT RUN IR GENERATOR - LEXER FAILED FIRST!\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "LEXER ERRORS:\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            elif self.engine.stopped_at == "Parser":
                self.output_text.insert(tk.END, "❌ CANNOT RUN IR GENERATOR - PARSER FAILED FIRST!\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "PARSER ERRORS:\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            elif self.engine.stopped_at == "Semantic Analyzer":
                self.output_text.insert(tk.END, "❌ CANNOT RUN IR GENERATOR - SEMANTIC ANALYZER FAILED FIRST!\n\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                self.output_text.insert(tk.END, "SEMANTIC ERRORS:\n")
                self.output_text.insert(tk.END, "=" * 80 + "\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            else:
                self.output_text.insert(tk.END, "❌ IR GENERATOR FAILED\n\n")
                for err in self.engine.errors:
                    self.output_text.insert(tk.END, f"{err}\n")
            self.status_label.config(text="❌ IR Generator failed")
            return
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "LEXER OUTPUT (Tokens):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team1_lexer(self.engine, self.output_text)
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "PARSER OUTPUT (AST):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team2_topdown_parser(self.engine, self.output_text)
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
        
        self.output_text.insert(tk.END, "=" * 80 + "\n")
        self.output_text.insert(tk.END, "SEMANTIC OUTPUT (Symbol Table):\n")
        self.output_text.insert(tk.END, "=" * 80 + "\n\n")
        team4_semantic(self.engine, self.output_text)
        self.output_text.insert(tk.END, "\n" + "=" * 80 + "\n\n")
        
        team5_ir_generator(self.engine, self.output_text)
        self.status_label.config(text="✅ Team 5 - IR Generator completed")
    
    def run_theory(self):
        self.clear_output()
        ir_theory_only(self.output_text)
        self.status_label.config(text="IR Theory displayed")


def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()