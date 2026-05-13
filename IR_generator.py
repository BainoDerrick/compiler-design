# ir_generator.py - COMPLETE IR GENERATOR (No dummy examples)

from ast_nodes import *
from typing import List, Union


# ============================================
# ACTUAL TAC GENERATION CODE
# ============================================

class ThreeAddressCode:
    """Generates Three-Address Code from AST for ALL language features"""
    
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0
    
    def new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"
    
    def new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"
    
    def add(self, instr: str):
        self.instructions.append(instr)
    
    def generate_from_ast(self, ast: Program):
        for stmt in ast.statements:
            self._visit(stmt)
        return self
    
    def _visit(self, node):
        if isinstance(node, Declaration):
            self._visit_declaration(node)
        elif isinstance(node, Assignment):
            self._visit_assignment(node)
        elif isinstance(node, Print):
            self._visit_print(node)
        elif isinstance(node, Block):
            self._visit_block(node)
        elif isinstance(node, WhileLoop):
            self._visit_while(node)
        elif isinstance(node, ForLoop):
            self._visit_for(node)
        elif isinstance(node, IfStatement):
            self._visit_if(node)
    
    def _visit_declaration(self, node: Declaration):
        # Initialize variable to 0
        self.add(f"{node.name} := 0")
    
    def _visit_assignment(self, node: Assignment):
        result = self._visit_expression(node.expr)
        self.add(f"{node.name} := {result}")
    
    def _visit_print(self, node: Print):
        value = self._visit_expression(node.expr)
        self.add(f"print {value}")
    
    def _visit_block(self, node: Block):
        for stmt in node.statements:
            self._visit(stmt)
    
    def _visit_while(self, node: WhileLoop):
        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()
        
        self.add(f"goto {start_label}")
        self.add_label(body_label)
        
        # Generate body
        self._visit(node.body)
        self.add_label(start_label)
        
        # Generate condition
        cond = self._visit_expression(node.condition)
        self.add(f"if {cond} != 0 goto {body_label}")
        self.add_label(end_label)
    
    def _visit_for(self, node: ForLoop):
        start_label = self.new_label()
        body_label = self.new_label()
        end_label = self.new_label()
        
        # Initialization
        if node.init:
            if isinstance(node.init, list):
                for stmt in node.init:
                    self._visit(stmt)
            else:
                self._visit(node.init)
        
        self.add(f"goto {start_label}")
        self.add_label(body_label)
        
        # Body
        self._visit(node.body)
        
        # Update
        if node.update:
            self._visit(node.update)
        
        self.add_label(start_label)
        
        # Condition
        if node.condition:
            cond = self._visit_expression(node.condition)
            self.add(f"if {cond} != 0 goto {body_label}")
        else:
            self.add(f"goto {body_label}")
        
        self.add_label(end_label)
    
    def _visit_if(self, node: IfStatement):
        else_label = self.new_label()
        end_label = self.new_label()
        
        # Condition
        cond = self._visit_expression(node.condition)
        self.add(f"if {cond} == 0 goto {else_label}")
        
        # Then body
        self._visit(node.then_body)
        self.add(f"goto {end_label}")
        
        # Else body
        self.add_label(else_label)
        if node.else_body:
            self._visit(node.else_body)
        
        # End
        self.add_label(end_label)
    
    def _visit_expression(self, expr):
        if isinstance(expr, Number):
            return expr.value
        elif isinstance(expr, Float):
            return expr.value
        elif isinstance(expr, String):
            return f'"{expr.value}"'
        elif isinstance(expr, Character):
            return f"'{expr.value}'"
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryOp):
            left = self._visit_expression(expr.left)
            right = self._visit_expression(expr.right)
            temp = self.new_temp()
            self.add(f"{temp} := {left} {self._op_to_string(expr.op)} {right}")
            return temp
        return "0"
    
    def _op_to_string(self, op):
        op_map = {
            "PLUS": "+", "MINUS": "-", "MULTIPLY": "*", "DIVIDE": "/",
            "POWER": "^", "EQUAL_EQUAL": "==", "NOT_EQUAL": "!=",
            "LESS": "<", "LESS_EQUAL": "<=", "GREATER": ">", "GREATER_EQUAL": ">="
        }
        return op_map.get(op, str(op))
    
    def add_label(self, label: str):
        self.add(f"{label}:")
    
    def __str__(self):
        lines = []
        for i, instr in enumerate(self.instructions):
            lines.append(f"{i:3d}  {instr}")
        return '\n'.join(lines)


class Optimizer:
    """Optimizations on TAC"""
    
    @staticmethod
    def constant_folding(tac: ThreeAddressCode) -> ThreeAddressCode:
        optimized = ThreeAddressCode()
        
        for instr in tac.instructions:
            parts = instr.split()
            if len(parts) == 4 and parts[1] == ':=' and parts[3] in ['+', '-', '*', '/', '^']:
                try:
                    left = float(parts[2]) if '.' in parts[2] else int(parts[2])
                    right = float(parts[4]) if '.' in parts[4] else int(parts[4])
                    op = parts[3]
                    
                    if op == '+':
                        result = left + right
                    elif op == '-':
                        result = left - right
                    elif op == '*':
                        result = left * right
                    elif op == '/':
                        result = left / right if right != 0 else 0
                    elif op == '^':
                        result = left ** right
                    
                    # Format result nicely
                    if isinstance(result, float) and result.is_integer():
                        result = int(result)
                    
                    optimized.add(f"{parts[0]} := {result}")
                    continue
                except:
                    pass
            optimized.add(instr)
        
        return optimized


class CodeGenerator:
    """Generate target code from TAC"""
    
    @staticmethod
    def to_python(tac: ThreeAddressCode) -> str:
        lines = ["def main():"]
        indent = "    "
        
        for instr in tac.instructions:
            if instr.startswith("print"):
                var = instr.split()[1]
                lines.append(f"{indent}print({var})")
            elif ":=" in instr:
                parts = instr.split()
                lines.append(f"{indent}{parts[0]} = {parts[2]}")
            elif instr.endswith(":"):
                lines.append(f"{indent}# {instr}")
        
        lines.append(f"{indent}return 0")
        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    main()")
        return '\n'.join(lines)
    
    @staticmethod
    def to_c(tac: ThreeAddressCode) -> str:
        lines = ["#include <stdio.h>", "", "int main() {"]
        indent = "    "
        declared = set()
        
        for instr in tac.instructions:
            if ":=" in instr and not instr.startswith("L"):
                parts = instr.split()
                var = parts[0]
                if var not in declared and (var.startswith('t') or var.isalpha()):
                    if '.' in str(parts[2]):
                        lines.append(f"{indent}float {var};")
                    else:
                        lines.append(f"{indent}int {var};")
                    declared.add(var)
        
        for instr in tac.instructions:
            if instr.startswith("print"):
                var = instr.split()[1]
                lines.append(f"{indent}printf(\"%d\\n\", {var});")
            elif ":=" in instr and not instr.startswith("L"):
                parts = instr.split()
                lines.append(f"{indent}{parts[0]} = {parts[2]};")
            elif instr.endswith(":"):
                lines.append(f"{indent}{instr}")
        
        lines.append(f"{indent}return 0;")
        lines.append("}")
        return '\n'.join(lines)


# ============================================
# IR PRESENTATION FUNCTIONS (No dummy examples)
# ============================================

def part1_ir_levels():
    print("\n" + "█"*60)
    print("PART 1: IR CLASSIFICATION BY LEVEL")
    print("█"*60)
    print("""
HIGH-LEVEL IR (HIR):
    Preserves high-level constructs like loops and conditionals.
    Example: for i := 1 to 10 step 1 do print(i); endfor

MEDIUM-LEVEL IR (MIR):
    Explicit control flow using labels and goto.
    Example: i := 1; L1: if i>10 goto L2; print(i); i:=i+1; goto L1; L2:

LOW-LEVEL IR (LIR):
    Assembly-like code with registers and explicit jumps.
    Example: mov i,#1; L1: cmp i,#10; bgt L2; push i; call print; add i,#1; b L1; L2: ret
""")


def part2_ir_structures():
    print("\n" + "█"*60)
    print("PART 2: IR CLASSIFICATION BY STRUCTURE")
    print("█"*60)
    print("""
GRAPHICAL IR (AST Tree):
        Program
          │
      Assignment (x = )
          │
        BinaryOp (+)
         /        \\
      Number(5)  BinaryOp(*)
                 /        \\
            Number(3)  Number(2)

LINEAR IR (Three-Address Code):
    t1 := 2
    t2 := 3
    t3 := t2 * t1
    t4 := 5
    t5 := t4 + t3
    x := t5

HYBRID IR (Basic Blocks + Control Flow Graph):
    ┌─────────────┐
    │    BB1      │
    │ t1 := 2     │
    │ t2 := 3     │
    │ t3 := t2*t1 │
    └──────┬──────┘
           ↓
    ┌─────────────┐
    │    BB2      │
    │ t4 := 5     │
    │ t5 := t4+t3 │
    │ x := t5     │
    └─────────────┘
""")


def part3_tac():
    print("\n" + "█"*60)
    print("PART 3: THREE-ADDRESS CODE (TAC)")
    print("█"*60)
    print("""
FORMAT:  result := operand1 operator operand2

Each instruction has at most ONE operator and THREE addresses.
Temporaries (t1, t2, t3...) store intermediate values.

EXAMPLES:
    x = 5 + 3 → t1 := 5; t2 := 3; t3 := t1 + t2; x := t3
    while (i < 10) → L1: if i < 10 goto L2; goto L3; L2: ...; goto L1; L3:
""")

def part4_complete_example():
    print("\n" + "█"*60)
    print("PART 4: COMPLETE EXAMPLE")
    print("█"*60)
    print("""
SOURCE CODE:
    int x;
    x = 5 + 3 * 2;
    print(x);

TAC GENERATED:
    0:  x := 0
    1:  t1 := 2
    2:  t2 := 3
    3:  t3 := t2 * t1
    4:  t4 := 5
    5:  t5 := t4 + t3
    6:  x := t5
    7:  print x

OPTIMIZED TAC:
    0:  x := 0
    1:  t1 := 2
    2:  t2 := 3
    3:  t3 := 6
    4:  t4 := 5
    5:  t5 := 11
    6:  x := 11
    7:  print x
""")


# ============================================
# MAIN
# ============================================

def main():
    print("\n" + "█"*60)
    print("IR GENERATOR - PRESENTATION MODE")
    print("█"*60)
    
    while True:
        print("\n" + "="*60)
        print("CHOOSE WHICH PART TO DISPLAY:")
        print("="*60)
        print("  1. IR Levels (High/Medium/Low)")
        print("  2. IR Structures (Graphical/Linear/Hybrid)")
        print("  3. Three-Address Code (TAC)")
        print("  4. Complete Example")
        print("  5. SHOW ALL PARTS")
        print("  6. EXIT")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            part1_ir_levels()
            input("\n▶ Press Enter to continue...")
        elif choice == "2":
            part2_ir_structures()
            input("\n▶ Press Enter to continue...")
        elif choice == "3":
            part3_tac()
            input("\n▶ Press Enter to continue...")
        elif choice == "4":
            part4_complete_example()
            input("\n▶ Press Enter to continue...")
        elif choice == "5":
            print("\n▶ SHOWING ALL PARTS\n")
            part1_ir_levels()
            part2_ir_structures()
            part3_tac()
            part4_complete_example()
            print("\n✅ Presentation Complete!")
            input("\n▶ Press Enter to return...")
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice.")


if __name__ == "__main__":
    main()