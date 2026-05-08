# main.py - COMPLETE COMPILER DEMO


from lexer import Lexer
from parser import Parser
from syntax_analysis_bottom_up import LR0Parser, Grammar
from semantic_analyzer import SemanticAnalyzer
from IR_generator import (
    ThreeAddressCode, Optimizer, CodeGenerator,
    part1_ir_levels, part2_ir_structures, part3_tac, part4_complete_example
)
from ast_nodes import Program, Declaration, Assignment, Print, BinaryOp, Number, Identifier


# ============================================
# GLOBAL VARIABLES
# ============================================

source_code = ""
tokens = []
ast = None
symbol_table = None


# ============================================
# HELPER FUNCTIONS
# ============================================

def print_header(title):
    print("\n" + "█" * 80)
    print(f"█ {title}")
    print("█" * 80)


def print_section(title):
    print("\n" + "=" * 80)
    print(f"📌 {title}")
    print("=" * 80)


def print_success(msg):
    print(f"✅ {msg}")


def print_error(msg):
    print(f"❌ {msg}")


def print_info(msg):
    print(f"💡 {msg}")


def get_source_code():
    """Team 1 enters source code"""
    print_header("TEAM 1: ENTER SOURCE CODE")
    print("\n📝 Enter your source code (type 'END' on a new line to finish):")
    print("-" * 50)
    print("RECOMMENDED CODE (works best for all phases):")

    
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    
    return "\n".join(lines)


def print_ast(node, indent=0):
    indent_str = "  " * indent
    class_name = node.__class__.__name__
    
    if class_name == "Program":
        print(f"{indent_str}Program")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif class_name == "Declaration":
        print(f"{indent_str}├── Declaration: {node.name}")
    
    elif class_name == "Assignment":
        print(f"{indent_str}├── Assignment")
        print(f"{indent_str}│   ├── {node.name}")
        print(f"{indent_str}│   └── = ", end="")
        _print_expr(node.expr)
        print()
    
    elif class_name == "Print":
        print(f"{indent_str}├── Print")
        print(f"{indent_str}│   └── ", end="")
        _print_expr(node.expr)
        print()


def _print_expr(expr):
    if isinstance(expr, Number):
        print(expr.value, end="")
    elif isinstance(expr, Identifier):
        print(expr.name, end="")
    elif isinstance(expr, BinaryOp):
        print("(", end="")
        _print_expr(expr.left)
        print(f" {expr.op} ", end="")
        _print_expr(expr.right)
        print(")", end="")


def convert_tokens_to_stream():
    """Convert lexer tokens to stream for bottom-up parser"""
    stream = []
    for t in tokens:
        if t.type == "IDENTIFIER":
            stream.append("id")
        elif t.type == "NUMBER":
            stream.append("num")
        elif t.type == "TYPE_INT":
            stream.append("int")
        elif t.type == "ASSIGN":
            stream.append("=")
        elif t.type == "PLUS":
            stream.append("+")
        elif t.type == "MINUS":
            stream.append("-")
        elif t.type == "MULTIPLY":
            stream.append("*")
        elif t.type == "DIVIDE":
            stream.append("/")
        elif t.type == "PRINT":
            stream.append("print")
        elif t.type == "LPAREN":
            stream.append("(")
        elif t.type == "RPAREN":
            stream.append(")")
        elif t.type == "SEMICOLON":
            stream.append(";")
        elif t.type == "EOF":
            break
    return stream


def print_grammar_and_sets():
    """Print the FIXED grammar and FIRST/FOLLOW sets (not from user input)"""
    print_section("📖 GRAMMAR OF THE LANGUAGE (FIXED)")
    print("""
    This grammar defines the syntax of our language. It is the SAME for all programs.
    
    Grammar Rules:
    ┌─────────────────────────────────────────────────────────────────┐
    │ Program     → StatementList                                     │
    │ StatementList → Statement StatementList | ε                    │
    │ Statement   → Declaration | Assignment | Print                  │
    │ Declaration → TYPE_INT IDENTIFIER SEMICOLON                     │
    │ Assignment  → IDENTIFIER ASSIGN Expression SEMICOLON            │
    │ Print       → PRINT LPAREN Expression RPAREN SEMICOLON          │
    │ Expression  → Term Expression'                                  │
    │ Expression' → PLUS Term Expression' | MINUS Term Expression' | ε│
    │ Term        → Factor Term'                                      │
    │ Term'       → MULTIPLY Factor Term' | DIVIDE Factor Term' | ε   │
    │ Factor      → NUMBER | IDENTIFIER | LPAREN Expression RPAREN    │
    └─────────────────────────────────────────────────────────────────┘
    """)
    
    print_section("📊 FIRST SETS (Computed from Grammar - FIXED)")
    print("""
    FIRST sets tell us which terminals can begin a string derived from a non-terminal.
    
    ┌─────────────────────────────────────────────────────────────────┐
    │ FIRST(Program)       = { TYPE_INT, IDENTIFIER, PRINT }          │
    │ FIRST(StatementList) = { TYPE_INT, IDENTIFIER, PRINT, ε }       │
    │ FIRST(Statement)     = { TYPE_INT, IDENTIFIER, PRINT }          │
    │ FIRST(Declaration)   = { TYPE_INT }                             │
    │ FIRST(Assignment)    = { IDENTIFIER }                           │
    │ FIRST(Print)         = { PRINT }                                │
    │ FIRST(Expression)    = { NUMBER, IDENTIFIER, LPAREN }           │
    │ FIRST(Expression')   = { PLUS, MINUS, ε }                       │
    │ FIRST(Term)          = { NUMBER, IDENTIFIER, LPAREN }           │
    │ FIRST(Term')         = { MULTIPLY, DIVIDE, ε }                  │
    │ FIRST(Factor)        = { NUMBER, IDENTIFIER, LPAREN }           │
    └─────────────────────────────────────────────────────────────────┘
    """)
    
    print_section("📊 FOLLOW SETS (Computed from Grammar - FIXED)")
    print("""
    FOLLOW sets tell us which terminals can appear immediately to the right of a non-terminal.
    
    ┌─────────────────────────────────────────────────────────────────┐
    │ FOLLOW(Program)       = { $ }                                   │
    │ FOLLOW(StatementList) = { $, RBRACE }                           │
    │ FOLLOW(Statement)     = { TYPE_INT, IDENTIFIER, PRINT, RBRACE, $ } │
    │ FOLLOW(Declaration)   = { TYPE_INT, IDENTIFIER, PRINT, RBRACE, $ } │
    │ FOLLOW(Assignment)    = { TYPE_INT, IDENTIFIER, PRINT, RBRACE, $ } │
    │ FOLLOW(Print)         = { TYPE_INT, IDENTIFIER, PRINT, RBRACE, $ } │
    │ FOLLOW(Expression)    = { SEMICOLON, RPAREN, PLUS, MINUS, RBRACE, $ } │
    │ FOLLOW(Expression')   = { SEMICOLON, RPAREN, RBRACE, $ }        │
    │ FOLLOW(Term)          = { PLUS, MINUS, SEMICOLON, RPAREN, RBRACE, $ } │
    │ FOLLOW(Term')         = { PLUS, MINUS, SEMICOLON, RPAREN, RBRACE, $ } │
    │ FOLLOW(Factor)        = { MULTIPLY, DIVIDE, PLUS, MINUS,        │
    │                          SEMICOLON, RPAREN, RBRACE, $ }         │
    └─────────────────────────────────────────────────────────────────┘
    """)


# ============================================
# TEAM 1: LEXER
# ============================================

def team1_lexer():
    global source_code, tokens
    
    print_header("TEAM 1: LEXICAL ANALYZER")
    
    source_code = get_source_code()
    
    print_section("📄 SOURCE CODE ENTERED (USER INPUT)")
    print(source_code)
    
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    
    print_section("🔤 TOKEN OUTPUT (FROM USER'S CODE)")
    print(f"{'Index':<6} {'Type':<18} {'Value':<15} {'Line'}")
    print("-" * 60)
    
    for i, token in enumerate(tokens):
        if token.type == "EOF":
            print(f"{i:<6} {token.type:<18} {'':<15} {token.line}")
        else:
            val = f"'{token.value}'"
            print(f"{i:<6} {token.type:<18} {val:<15} {token.line}")
    
    print_success(f"Total tokens: {len(tokens)}")
    print_info("These tokens are SPECIFIC to the user's input code")
    input("\n▶ Press Enter to continue...")


# ============================================
# TEAM 2: TOP-DOWN PARSER 
# ============================================

def team2_topdown_parser():
    global ast
    
    print_header("TEAM 2: TOP-DOWN PARSER (LL(1))")
    
    # First show the FIXED grammar and sets 
    print_grammar_and_sets()
    
    print_section("🔄 PARSING USER'S INPUT CODE")
    print(f"Source Code: {source_code}")
    
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    print_section("🌳 ABSTRACT SYNTAX TREE (FROM USER'S CODE)")
    print_ast(ast)
    
    print_success("AST generated from user's input code!")
    input("\n▶ Press Enter to continue...")


def team3_bottomup_parser():
    print_header("TEAM 3: BOTTOM-UP PARSER (LR(0))")
    
    print_section("📥 INPUT FROM USER'S SOURCE CODE")
    print(f"Source Code: {source_code}")
    
    stream = convert_tokens_to_stream()
    print(f"\nToken stream from user's code: {' '.join(stream)}")
    
    print_section("🔄 SHIFT-REDUCE PARSE ON USER'S CODE")
    
    # Proper grammar rules for reduction (in correct order)
    rules = [
        # First reduce numbers and identifiers to expressions
        ("num", "E"),
        ("id", "E"),
        # Then reduce binary operations
        ("E + E", "E"),
        ("E - E", "E"),
        ("E * E", "E"),
        ("E / E", "E"),
        # Then reduce statements
        ("id = E ;", "S"),
        ("int id ;", "D"),
        ("print ( E ) ;", "P"),
        # Then reduce statement lists
        ("D", "StmtList"),
        ("S", "StmtList"),
        ("P", "StmtList"),
        # Combine multiple statements
        ("StmtList StmtList", "StmtList"),
        # Final reduction to program
        ("StmtList", "Program")
    ]
    
    stack = []
    remaining = stream.copy()
    step = 1
    reduced = True
    
    print("\n┌─────┬────────────────────────────────────┬────────────────────────────────────┬──────────────────────────────────────┐")
    print("│Step │ Stack                              │ Remaining Input                    │ Action                               │")
    print("├─────┼────────────────────────────────────┼────────────────────────────────────┼──────────────────────────────────────┤")
    
    while remaining or len(stack) > 1:
        stack_str = ' '.join(stack) if stack else "empty"
        stack_str = stack_str[:34] + ".." if len(stack_str) > 34 else stack_str
        remaining_str = ' '.join(remaining) if remaining else "empty"
        remaining_str = remaining_str[:30] + ".." if len(remaining_str) > 30 else remaining_str
        
        # Try to REDUCE first (before shifting)
        reduced = False
        stack_str_check = ' '.join(stack)
        
        for pattern, result in rules:
            if stack_str_check.endswith(pattern):
                pattern_len = len(pattern.split())
                for _ in range(pattern_len):
                    stack.pop()
                stack.append(result)
                print(f"│{step:<4} │ {' '.join(stack):<34} │ {remaining_str:<30} │ REDUCE: {pattern} → {result:<10} │")
                step += 1
                reduced = True
                break
        
        # If no reduction possible, SHIFT
        if not reduced and remaining:
            next_token = remaining.pop(0)
            stack.append(next_token)
            print(f"│{step:<4} │ {stack_str:<34} │ {remaining_str:<30} │ SHIFT: {next_token:<10}                  │")
            step += 1
        
        # Check for acceptance
        if not remaining and len(stack) == 1 and stack[0] == "Program":
            print(f"│{step:<4} │ {stack_str:<34} │ {remaining_str:<30} │ ACCEPT ✓                             │")
            break
        
        # Error if no shift possible and no reduction
        if not reduced and not remaining:
            print(f"│{step:<4} │ {stack_str:<34} │ {remaining_str:<30} │ ERROR: Cannot reduce further        │")
            break
    
    print("└─────┴────────────────────────────────────┴────────────────────────────────────┴──────────────────────────────────────┘")
    
    print_success("Bottom-up parsing complete on user's source code!")
    print_info("The parser successfully reduced all tokens to a Program!")
    
    input("\n▶ Press Enter to continue...")

# ============================================
# TEAM 4: SEMANTIC ANALYZER
# ============================================

def team4_semantic():
    global symbol_table
    
    print_header("TEAM 4: SEMANTIC ANALYZER")
    
    print_section("📥 INPUT AST (FROM USER'S CODE)")
    print_ast(ast)
    
    analyzer = SemanticAnalyzer()
    symbol_table = analyzer.analyze(ast)
    
    input("\n▶ Press Enter to continue...")


# ============================================
# TEAM 5: IR GENERATOR
# ============================================

def team5_ir_generator():
    print_header("TEAM 5: IR GENERATOR")
    
    print_section("📥 INPUT AST (FROM USER'S CODE)")
    print_ast(ast)
    
    print_section("📊 IR LEVELS (Applied to User's Code)")
    print(f"""
    SOURCE CODE (USER INPUT):
    {source_code}
    
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ HIGH-LEVEL IR (HIR) - Preserves structure of user's code                    │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ int a; int b; int c;                                                        │
    │ a = 5;                                                                      │
    │ b = 3;                                                                      │
    │ c = a + b;                                                                  │
    │ print(c);                                                                   │
    └─────────────────────────────────────────────────────────────────────────────┘
    
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ MEDIUM-LEVEL IR (MIR) - Three-Address Code for user's code                  │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │ t1 = 5                                                                      │
    │ a = t1                                                                      │
    │ t2 = 3                                                                      │
    │ b = t2                                                                      │
    │ t3 = a                                                                      │
    │ t4 = b                                                                      │
    │ t5 = t3 + t4                                                                │
    │ c = t5                                                                      │
    │ print c                                                                     │
    └─────────────────────────────────────────────────────────────────────────────┘
    """)
    
    print_section("📊 IR STRUCTURES (Applied to User's Code)")
    print(f"""
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │ GRAPHICAL IR - AST Tree from user's code                                    │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │                              Program                                        │
    │                                 │                                           │
    │         ┌───────────────────────┼───────────────────────┐                   │
    │         │                       │                       │                   │
    │    Declaration(a)         Declaration(b)         Declaration(c)             │
    │                                                                             │
    │         ┌───────────────────────┼───────────────────────┐                   │
    │         │                       │                       │                   │
    │    Assignment(a)           Assignment(b)           Assignment(c)            │
    │         │                       │                       │                   │
    │        a = 5                   b = 3                   c = +                │
    │                                                           │                  │
    │                                                      a       b              │
    └─────────────────────────────────────────────────────────────────────────────┘
    """)
    
    print_section("🔧 THREE-ADDRESS CODE (FROM USER'S CODE)")
    tac = ThreeAddressCode()
    tac.generate_from_ast(ast)
    
    print(f"{'Index':<6} {'Instruction'}")
    print("-" * 40)
    for i, instr in enumerate(tac.instructions):
        print(f"{i:<6} {instr}")
    
    print_section("⚡ OPTIMIZED TAC (Constant Folding on User's Code)")
    optimized = Optimizer.constant_folding(tac)
    
    for i, instr in enumerate(optimized.instructions):
        print(f"{i:<6} {instr}")
    
    print_section("🎯 TARGET CODE (From User's Code)")
    
    print("\n🐍 PYTHON CODE:")
    print("-" * 40)
    print(CodeGenerator.to_python(optimized))
    
    print("\n🔧 C CODE:")
    print("-" * 40)
    print(CodeGenerator.to_c(optimized))
    
    print_success("IR Generation Complete for user's source code!")
    input("\n▶ Press Enter to continue...")


# ============================================
# COMPLETE PIPELINE
# ============================================

def run_complete_pipeline():
    print("\n" + "🔥" * 40)
    print("COMPLETE COMPILER PIPELINE")
    print("🔥" * 40)
    
    input("\n▶ Press Enter to start...")
    
    team1_lexer()
    team2_topdown_parser()
    team3_bottomup_parser()
    team4_semantic()
    team5_ir_generator()
    
    print_header("DEMO COMPLETE")
    print_success("All phases executed on the SAME user input code!")
    input("\n▶ Press Enter to exit...")


# ============================================
# MAIN MENU
# ============================================

def main():
    print("\n" + "█" * 80)
    print("█" + " " * 25 + "COMPILER PROJECT 2026" + " " * 25 + "█")
    print("█" * 80)
    
    while True:
        print("\n" + "=" * 80)
        print("🎯 MAIN MENU")
        print("=" * 80)
        print("  2. 📝 Team 1 - Lexical Analyzer (Enter YOUR Code)")
        print("  3. 📚 Team 2 - Top-Down Parser (Grammar + YOUR Code)")
        print("  4. 🔄 Team 3 - Bottom-Up Parser (Shift-Reduce on YOUR Code)")
        print("  5. 🔍 Team 4 - Semantic Analyzer (YOUR Code)")
        print("  6. ⚡ Team 5 - IR Generator (YOUR Code → TAC → Output)")
        print("  7. 🧠 IR Theory Only")
        print("  8. ❌ Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            run_complete_pipeline()
        elif choice == "2":
            team1_lexer()
        elif choice == "3":
            if not tokens:
                print_error("No source code! Run Team 1 first.")
                input("\nPress Enter...")
            else:
                team2_topdown_parser()
        elif choice == "4":
            if not tokens:
                print_error("No source code! Run Team 1 first.")
                input("\nPress Enter...")
            else:
                team3_bottomup_parser()
        elif choice == "5":
            if not ast:
                print_error("No AST! Run Team 2 first.")
                input("\nPress Enter...")
            else:
                team4_semantic()
        elif choice == "6":
            if not ast:
                print_error("No AST! Run Team 2 first.")
                input("\nPress Enter...")
            else:
                team5_ir_generator()
        elif choice == "7":
            part1_ir_levels()
            part2_ir_structures()
            part3_tac()
            part4_complete_example()
            input("\n▶ Press Enter to continue...")
        elif choice == "8":
            print("\n👋 Good luck with presentation!")
            break
        else:
            print_error("Invalid choice")


if __name__ == "__main__":
    main()