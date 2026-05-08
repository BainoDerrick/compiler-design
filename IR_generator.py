# ir_generator.py - COMPLETE IR GENERATOR
# Contains: Presentation Parts + Actual TAC Generation Code

from ast_nodes import Program, Declaration, Assignment, Print, BinaryOp, Number, Identifier
from typing import List, Union


# ============================================
# ACTUAL TAC GENERATION CODE (For main.py)
# ============================================

class ThreeAddressCode:
    """Generates Three-Address Code from AST"""
    
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
            self.add(f"{node.name} := 0")
        elif isinstance(node, Assignment):
            result = self._visit_expression(node.expr)
            self.add(f"{node.name} := {result}")
        elif isinstance(node, Print):
            value = self._visit_expression(node.expr)
            self.add(f"print {value}")
    
    def _visit_expression(self, expr):
        if isinstance(expr, Number):
            temp = self.new_temp()
            self.add(f"{temp} := {expr.value}")
            return temp
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryOp):
            left = self._visit_expression(expr.left)
            right = self._visit_expression(expr.right)
            temp = self.new_temp()
            self.add(f"{temp} := {left} {expr.op} {right}")
            return temp
        return "0"
    
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
            # Check for constant operations like: t3 := 3 * 2
            parts = instr.split()
            if len(parts) == 4 and parts[1] == ':=' and parts[3] in ['+', '-', '*', '/']:
                try:
                    left = int(parts[2])
                    right = int(parts[4])
                    op = parts[3]
                    
                    if op == '+':
                        result = left + right
                    elif op == '-':
                        result = left - right
                    elif op == '*':
                        result = left * right
                    elif op == '/':
                        result = left // right if right != 0 else 0
                    
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
            if ":=" in instr:
                parts = instr.split()
                var = parts[0]
                if var not in declared and var.startswith('t'):
                    lines.append(f"{indent}int {var};")
                    declared.add(var)
        
        for instr in tac.instructions:
            if instr.startswith("print"):
                var = instr.split()[1]
                lines.append(f"{indent}printf(\"%d\\n\", {var});")
            elif ":=" in instr:
                parts = instr.split()
                lines.append(f"{indent}{parts[0]} = {parts[2]};")
        
        lines.append(f"{indent}return 0;")
        lines.append("}")
        return '\n'.join(lines)


# ============================================
# PART 1: IR LEVELS
# ============================================

def part1_ir_levels():
    print("\n" + "█"*60)
    print("PART 1: IR CLASSIFICATION BY LEVEL")
    print("█"*60)
    print("""
HIGH-LEVEL IR (HIR):
    for i := 1 to 10 step 1 do
        print(i);
    endfor

MEDIUM-LEVEL IR (MIR):
    i := 1
L1: if i > 10 goto L2
    print(i)
    i := i + 1
    goto L1
L2:

LOW-LEVEL IR (LIR):
    mov i, #1
L1: cmp i, #10
    bgt L2
    push i
    call print
    add i, i, #1
    b L1
L2: ret
""")


# ============================================
# PART 2: IR STRUCTURES
# ============================================

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
      Num(5)    BinaryOp(*)
                /        \\
            Num(3)     Num(2)

LINEAR IR (Three-Address Code):
    t1 := 2
    t2 := 3
    t3 := t2 * t1
    t4 := 5
    t5 := t4 + t3
    x := t5

HYBRID IR (Basic Blocks + CFG):
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


# ============================================
# PART 3: THREE-ADDRESS CODE (TAC)
# ============================================

def part3_tac():
    print("\n" + "█"*60)
    print("PART 3: THREE-ADDRESS CODE (TAC)")
    print("█"*60)
    print("""
FORMAT:  result := operand1 operator operand2

EXAMPLE: x = 5 + 3 * 2

STEP BY STEP:
    Step 1: t1 := 2      (load first constant)
    Step 2: t2 := 3      (load second constant)
    Step 3: t3 := t2 * t1 (multiplication first)
    Step 4: t4 := 5      (load constant)
    Step 5: t5 := t4 + t3 (addition)
    Step 6: x := t5       (assignment)

WHY t1, t2, t3?
    Each temporary holds ONE intermediate value.
    Makes translation to assembly easier.
""")


# ============================================
# PART 4: COMPLETE EXAMPLE
# ============================================

def part4_complete_example():
    print("\n" + "█"*60)
    print("PART 4: COMPLETE EXAMPLE - x = 5 + 3 * 2")
    print("█"*60)
    
    print("\n📝 SOURCE CODE:")
    print("    int x;")
    print("    x = 5 + 3 * 2;")
    print("    print(x);")
    
    print("\n🌳 STEP 1: AST (Graphical IR)")
    print("    Program")
    print("      Declaration: x")
    print("      Assignment: x =")
    print("                +")
    print("               / \\")
    print("              5   *")
    print("                 / \\")
    print("                3   2")
    print("      Print: x")
    
    print("\n📝 STEP 2: TAC (Linear IR)")
    print("    0    t1 := 2")
    print("    1    t2 := 3")
    print("    2    t3 := t2 * t1")
    print("    3    t4 := 5")
    print("    4    t5 := t4 + t3")
    print("    5    x := t5")
    print("    6    print x")
    
    print("\n📊 STEP 3: CFG (Hybrid IR)")
    print("    ┌─────────────────┐")
    print("    │      BB1        │")
    print("    │   t1 := 2       │")
    print("    │   t2 := 3       │")
    print("    │   t3 := t2 * t1 │")
    print("    │   t4 := 5       │")
    print("    │   t5 := t4 + t3 │")
    print("    │   x := t5       │")
    print("    │   print x       │")
    print("    └────────┬────────┘")
    print("             ↓")
    print("    ┌─────────────────┐")
    print("    │      Exit       │")
    print("    └─────────────────┘")
    
    print("\n⚡ STEP 4: Optimization (Constant Folding)")
    print("    0    t1 := 2")
    print("    1    t2 := 3")
    print("    2    t3 := 6       (3 * 2 computed)")
    print("    3    t4 := 5")
    print("    4    t5 := 11      (5 + 6 computed)")
    print("    5    x := 11")
    print("    6    print x")
    
    print("\n🎯 STEP 5: Generated Output")
    print("    x = 11")
    print("    11")


# ============================================
# MAIN FOR IR GENERATOR ONLY
# ============================================

def main():
    print("\n" + "█"*60)
    print("IR GENERATOR - 5 MINUTE PRESENTATION")
    print("█"*60)
    
    while True:
        print("\n" + "="*60)
        print("CHOOSE WHICH PART TO DISPLAY:")
        print("="*60)
        print("  1. PART 1 - IR Levels (High/Medium/Low)")
        print("  2. PART 2 - IR Structures (Graphical/Linear/Hybrid)")
        print("  3. PART 3 - Three-Address Code (TAC)")
        print("  4. PART 4 - Complete Example (All Steps)")
        print("  5. SHOW ALL PARTS (Auto-play)")
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
            print("\n" + "▶ SHOWING ALL PARTS - Press Enter after each part ◀")
            input("\nPress Enter to start...")
            part1_ir_levels()
            input("\n▶ Press Enter for PART 2...")
            part2_ir_structures()
            input("\n▶ Press Enter for PART 3...")
            part3_tac()
            input("\n▶ Press Enter for PART 4...")
            part4_complete_example()
            print("\n✅ Presentation Complete!")
            input("\n▶ Press Enter to return to menu...")
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()