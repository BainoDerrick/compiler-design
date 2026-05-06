# runs the compiler, allowing the user to input source code and see the resulting tokens and AST.

from lexer import Lexer
from parser import Parser

def main():
    print("Enter code (blank line to finish):")

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)

    source_code = "\n".join(lines)

    # Step 1: Lexical Analysis
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    print("\nTOKENS:")
    for token in tokens:
        print(token)

    # Step 2: Parsing
    parser = Parser(tokens)
    ast = parser.parse_program()

    print("\nAST:")
    print(ast)


if __name__ == "__main__":
    main()