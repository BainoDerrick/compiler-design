# LEXICAL ANALYZER (LEXER)
# Reads source code and produces tokens

class Token:
    """Represents a single token"""
    def __init__(self, type_, value, line, column):
        self.type = type_      # e.g., "NUMBER", "PLUS", "IDENTIFIER"
        self.value = value     # e.g., 42, "+", "variable_name"
        self.line = line       # line number (for error reporting)
        self.column = column   # column number
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, column={self.column})"


class Lexer:
    """Converts source code string into a list of tokens"""
    
    def __init__(self, source_code):
        self.source = source_code    # The raw input string
        self.position = 0            # Current character index
        self.line = 1                # Current line number
        self.column = 1              # Current column number
        self.tokens = []             # List to store generated tokens
    
    # ----- Helper methods to navigate the source code -----
    
    def current_char(self):
        """Return the current character, or None if at end"""
        if self.position < len(self.source):
            return self.source[self.position]
        return None
    
    def advance(self):
        """Move to next character, tracking line/column"""
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def peek_next_char(self):
        """Look at next character without moving"""
        if self.position + 1 < len(self.source):
            return self.source[self.position + 1]
        return None
    
    # ----- Methods to recognize and add tokens -----
    
    def add_token(self, type_, value=None):
        """Create a token and add it to our list"""
        token = Token(type_, value, self.line, self.column)
        self.tokens.append(token)
    
    def skip_whitespace(self):
        """Skip spaces, tabs, newlines (but track newlines)"""
        while self.current_char() and self.current_char().isspace():
            self.advance()  # advance() handles line counting
    
    def read_number(self):
        """Read a sequence of digits (integer)"""
        start_col = self.column
        num_str = ""
        while self.current_char() and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()
        self.add_token("NUMBER", int(num_str))
    
    def read_identifier_or_keyword(self):
        """Read letters/digits/underscore, check if it's a keyword"""
        start_col = self.column
        id_str = ""
        while self.current_char() and (self.current_char().isalpha() or self.current_char().isdigit() or self.current_char() == '_'):
            id_str += self.current_char()
            self.advance()
        
        # List of keywords in our language
        keywords = {
            "if": "IF",
            "else": "ELSE",
            "while": "WHILE",
            "return": "RETURN",
            "int": "TYPE_INT",
            "float": "TYPE_FLOAT",
            "string": "TYPE_STRING",
            "bool": "TYPE_BOOL",
            "true": "TRUE",
            "false": "FALSE",
            "print": "PRINT"
        }
        
        # Check if it's a keyword or a regular identifier
        if id_str in keywords:
            self.add_token(keywords[id_str], id_str)
        else:
            self.add_token("IDENTIFIER", id_str)
    
    def read_operator_or_symbol(self):
        """Handle operators and single-character symbols"""
        char = self.current_char()
        
        # Two-character operators like ==, !=, <=, >=
        if char == '=':
            if self.peek_next_char() == '=':
                self.advance()  # consume first '='
                self.advance()  # consume second '='
                self.add_token("EQUAL_EQUAL", "==")
            else:
                self.advance()
                self.add_token("ASSIGN", "=")
            return
        
        elif char == '!':
            if self.peek_next_char() == '=':
                self.advance()
                self.advance()
                self.add_token("NOT_EQUAL", "!=")
                return
            else:
                raise Exception(f"Invalid character '{char}' at line {self.line}, column {self.column}")
        
        elif char == '<':
            if self.peek_next_char() == '=':
                self.advance()
                self.advance()
                self.add_token("LESS_EQUAL", "<=")
            else:
                self.advance()
                self.add_token("LESS", "<")
            return
        
        elif char == '>':
            if self.peek_next_char() == '=':
                self.advance()
                self.advance()
                self.add_token("GREATER_EQUAL", ">=")
            else:
                self.advance()
                self.add_token("GREATER", ">")
            return
        
        # Single-character operators and symbols
        operators_symbols = {
            '+': "PLUS",
            '-': "MINUS",
            '*': "MULTIPLY",
            '/': "DIVIDE",
            '(': "LPAREN",
            ')': "RPAREN",
            '{': "LBRACE",
            '}': "RBRACE",
            ';': "SEMICOLON",
            ',': "COMMA",
            '?': "QUESTIONMARK",
            ':': "COLON"
            
        }
        
        if char in operators_symbols:
            self.add_token(operators_symbols[char], char)
            self.advance()
        else:
            raise Exception(f"Unknown character '{char}' at line {self.line}, column {self.column}")
    
    # ----- Main tokenization loop -----
    
    def tokenize(self):
        """Main method: read entire source and return token list"""
        while self.current_char():
            
            # 1. Skip whitespace
            if self.current_char().isspace():
                self.skip_whitespace()
                continue
            
            # 2. Handle numbers
            if self.current_char().isdigit():
                self.read_number()
                continue
            
            # 3. Handle identifiers and keywords (letters/underscore)
            if self.current_char().isalpha() or self.current_char() == '_':
                self.read_identifier_or_keyword()
                continue
            
            # 4. Handle operators and symbols
            self.read_operator_or_symbol()
        
        # Add end-of-file marker (optional, but good practice)
        self.add_token("EOF", None)
        return self.tokens


class RegexToken:
    """Token for regex parsing"""
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value


class RegexParser:
    """Parse regex into postfix tokens for Thompson NFA"""
    def __init__(self, regex):
        self.regex = regex
        self.position = 0

    def current_char(self):
        if self.position < len(self.regex):
            return self.regex[self.position]
        return None

    def advance(self):
        self.position += 1

    def read_char_class(self):
        chars = set()
        self.advance()  # skip '['
        prev = None
        while self.current_char() and self.current_char() != ']':
            ch = self.current_char()
            if ch == '\\' and self.peek_next_char():
                self.advance()
                ch = self.current_char()
                chars.add(ch)
                prev = ch
                self.advance()
                continue
            if ch == '-' and prev and self.peek_next_char() and self.peek_next_char() != ']':
                self.advance()
                end = self.current_char()
                for code in range(ord(prev), ord(end) + 1):
                    chars.add(chr(code))
                prev = None
                self.advance()
                continue
            chars.add(ch)
            prev = ch
            self.advance()
        if self.current_char() != ']':
            raise Exception("Unterminated character class")
        self.advance()  # skip ']'
        return chars

    def peek_next_char(self):
        if self.position + 1 < len(self.regex):
            return self.regex[self.position + 1]
        return None

    def tokenize(self):
        tokens = []
        while self.current_char():
            ch = self.current_char()
            if ch.isspace():
                self.advance()
                continue
            if ch == '[':
                chars = self.read_char_class()
                tokens.append(RegexToken("LITERAL", chars))
                continue
            if ch == '\\':
                self.advance()
                if not self.current_char():
                    raise Exception("Dangling escape in regex")
                tokens.append(RegexToken("LITERAL", {self.current_char()}))
                self.advance()
                continue
            if ch in {'|', '*', '(', ')'}:
                tokens.append(RegexToken(ch))
                self.advance()
                continue
            tokens.append(RegexToken("LITERAL", {ch}))
            self.advance()
        return tokens

    def insert_concatenation(self, tokens):
        result = []
        for i, tok in enumerate(tokens):
            result.append(tok)
            if i == len(tokens) - 1:
                continue
            a = tok.type
            b = tokens[i + 1].type
            if a in {"LITERAL", ')', '*'} and b in {"LITERAL", '('}:
                result.append(RegexToken('.'))
        return result

    def to_postfix(self):
        tokens = self.insert_concatenation(self.tokenize())
        output = []
        stack = []
        precedence = {'*': 3, '.': 2, '|': 1}

        for tok in tokens:
            if tok.type == "LITERAL":
                output.append(tok)
                continue
            if tok.type == '(':
                stack.append(tok)
                continue
            if tok.type == ')':
                while stack and stack[-1].type != '(':
                    output.append(stack.pop())
                if not stack:
                    raise Exception("Mismatched parentheses")
                stack.pop()
                continue
            if tok.type == '*':
                output.append(tok)
                continue

            while stack and stack[-1].type != '(' and precedence[stack[-1].type] >= precedence[tok.type]:
                output.append(stack.pop())
            stack.append(tok)

        while stack:
            if stack[-1].type in {'(', ')'}:
                raise Exception("Mismatched parentheses")
            output.append(stack.pop())
        return output


class NFA:
    """Simple NFA for regex to DFA conversion"""
    def __init__(self):
        self.transitions = {}
        self.next_state = 0

    def new_state(self):
        state = self.next_state
        self.next_state += 1
        self.transitions[state] = []
        return state

    def add_transition(self, from_state, to_state, symbols=None):
        self.transitions[from_state].append((symbols, to_state))


def build_nfa_from_postfix(postfix):
    nfa = NFA()
    stack = []

    for tok in postfix:
        if tok.type == "LITERAL":
            start = nfa.new_state()
            accept = nfa.new_state()
            nfa.add_transition(start, accept, tok.value)
            stack.append((start, accept))
        elif tok.type == '.':
            b_start, b_accept = stack.pop()
            a_start, a_accept = stack.pop()
            nfa.add_transition(a_accept, b_start, None)
            stack.append((a_start, b_accept))
        elif tok.type == '|':
            b_start, b_accept = stack.pop()
            a_start, a_accept = stack.pop()
            start = nfa.new_state()
            accept = nfa.new_state()
            nfa.add_transition(start, a_start, None)
            nfa.add_transition(start, b_start, None)
            nfa.add_transition(a_accept, accept, None)
            nfa.add_transition(b_accept, accept, None)
            stack.append((start, accept))
        elif tok.type == '*':
            a_start, a_accept = stack.pop()
            start = nfa.new_state()
            accept = nfa.new_state()
            nfa.add_transition(start, a_start, None)
            nfa.add_transition(start, accept, None)
            nfa.add_transition(a_accept, a_start, None)
            nfa.add_transition(a_accept, accept, None)
            stack.append((start, accept))
        else:
            raise Exception(f"Unsupported regex token: {tok.type}")

    if len(stack) != 1:
        raise Exception("Invalid regex: unable to reduce to single NFA")
    start, accept = stack.pop()
    return nfa, start, accept


def epsilon_closure(nfa, states):
    stack = list(states)
    closure = set(states)
    while stack:
        state = stack.pop()
        for symbols, next_state in nfa.transitions.get(state, []):
            if symbols is None and next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure


def move(nfa, states, ch):
    dest = set()
    for state in states:
        for symbols, next_state in nfa.transitions.get(state, []):
            if symbols is not None and ch in symbols:
                dest.add(next_state)
    return dest


def nfa_to_dfa(nfa, start_state, accept_state):
    alphabet = set()
    for edges in nfa.transitions.values():
        for symbols, _ in edges:
            if symbols is not None:
                alphabet.update(symbols)

    start_closure = frozenset(epsilon_closure(nfa, {start_state}))
    dfa_states = {start_closure: 0}
    dfa_transitions = {}
    dfa_accepting = set()
    unprocessed = [start_closure]

    if accept_state in start_closure:
        dfa_accepting.add(0)

    while unprocessed:
        current = unprocessed.pop()
        current_id = dfa_states[current]
        dfa_transitions[current_id] = {}

        for ch in sorted(alphabet):
            target = epsilon_closure(nfa, move(nfa, current, ch))
            if not target:
                continue
            target_fs = frozenset(target)
            if target_fs not in dfa_states:
                dfa_states[target_fs] = len(dfa_states)
                unprocessed.append(target_fs)
                if accept_state in target_fs:
                    dfa_accepting.add(dfa_states[target_fs])
            dfa_transitions[current_id][ch] = dfa_states[target_fs]

    return dfa_transitions, dfa_accepting


def build_nfa_mermaid_lines(nfa, start_state, accept_state):
    lines = ["stateDiagram-v2", "    %% NFA"]
    lines.append(f"    state S{accept_state} <<final>>")

    edge_labels = {}
    for from_state, edges in nfa.transitions.items():
        for symbols, to_state in edges:
            if symbols is None:
                label_text = "epsilon"
            else:
                label_text = ", ".join(sorted(symbols))
            key = (from_state, to_state)
            edge_labels.setdefault(key, []).append(label_text)

    for (from_state, to_state), labels in sorted(edge_labels.items()):
        label_text = ", ".join(labels)
        lines.append(f"    S{from_state} --> S{to_state}: {label_text}")

    return lines


def build_dfa_mermaid_lines(dfa_transitions, dfa_accepting):
    lines = ["stateDiagram-v2", "    %% DFA"]
    for state in sorted(dfa_accepting):
        lines.append(f"    state S{state} <<final>>")

    edge_labels = {}
    for from_state, transitions in dfa_transitions.items():
        for ch, to_state in transitions.items():
            key = (from_state, to_state)
            edge_labels.setdefault(key, []).append(ch)

    for (from_state, to_state), labels in sorted(edge_labels.items()):
        label_text = ", ".join(labels)
        lines.append(f"    S{from_state} --> S{to_state}: {label_text}")

    return lines


def write_nfa_and_dfa_mermaid(nfa, start_state, accept_state, dfa_transitions, dfa_accepting, output_path):
    nfa_lines = build_nfa_mermaid_lines(nfa, start_state, accept_state)
    dfa_lines = build_dfa_mermaid_lines(dfa_transitions, dfa_accepting)
    with open(output_path, "w", encoding="ascii") as f:
        f.write("\n".join(nfa_lines))
        f.write("\n\n")
        f.write("\n".join(dfa_lines))


def build_nfa_dot_lines(nfa, start_state, accept_state):
    lines = [
        "digraph NFA {",
        "    rankdir=LR;",
        "    node [shape=circle];",
    ]

    lines.append(f"    node [shape=doublecircle]; S{accept_state};")
    lines.append("    node [shape=circle];")

    edge_labels = {}
    for from_state, edges in nfa.transitions.items():
        for symbols, to_state in edges:
            if symbols is None:
                label_text = "epsilon"
            else:
                label_text = ", ".join(sorted(symbols))
            key = (from_state, to_state)
            edge_labels.setdefault(key, []).append(label_text)

    for (from_state, to_state), labels in sorted(edge_labels.items()):
        label_text = ", ".join(labels)
        lines.append(f"    S{from_state} -> S{to_state} [label=\"{label_text}\"]; ")

    lines.append("}")
    return lines


def build_dfa_dot_lines(dfa_transitions, dfa_accepting):
    lines = [
        "digraph DFA {",
        "    rankdir=LR;",
        "    node [shape=circle];",
    ]

    if dfa_accepting:
        accepting = " ".join([f"S{state}" for state in sorted(dfa_accepting)])
        lines.append(f"    node [shape=doublecircle]; {accepting};")
        lines.append("    node [shape=circle];")

    edge_labels = {}
    for from_state, transitions in dfa_transitions.items():
        for ch, to_state in transitions.items():
            key = (from_state, to_state)
            edge_labels.setdefault(key, []).append(ch)

    for (from_state, to_state), labels in sorted(edge_labels.items()):
        label_text = ", ".join(labels)
        lines.append(f"    S{from_state} -> S{to_state} [label=\"{label_text}\"]; ")

    lines.append("}")
    return lines


def write_nfa_and_dfa_dot(nfa, start_state, accept_state, dfa_transitions, dfa_accepting, output_path):
    nfa_lines = build_nfa_dot_lines(nfa, start_state, accept_state)
    dfa_lines = build_dfa_dot_lines(dfa_transitions, dfa_accepting)
    with open(output_path, "w", encoding="ascii") as f:
        f.write("\n".join(nfa_lines))
        f.write("\n\n")
        f.write("\n".join(dfa_lines))


# ----- DEMONSTRATION -----
if __name__ == "__main__":
    print("Enter source code to tokenize.")
    print("Input format guidance:")
    print("- Write code using tokens supported by this lexer.")
    print("- End statements with ';' where appropriate.")
    print("- Supported keywords: int, if, else, while, return, print")
    print("- Supported symbols/operators: + - * / = == != < <= > >= ( ) { } ; ,")
    print("- Enter a blank line to finish input.\n")

    choice = input("Type L for lexer, R for regex->DFA (or Q to quit): ").strip().upper()

    if choice == "L":
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)

        source = "\n".join(lines)

        if not source.strip():
            print("No source code entered. Exiting.")
        else:
            print("\nTOKENS:")
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            for token in tokens:
                print(token)
    elif choice == "R":
        regex = input("Enter a regex (e.g., a|st, s*, [0-9]): ").strip()
        if not regex:
            print("No regex entered. Exiting.")
        else:
            parser = RegexParser(regex)
            postfix = parser.to_postfix()
            nfa, nfa_start, nfa_accept = build_nfa_from_postfix(postfix)
            dfa_transitions, dfa_accepting = nfa_to_dfa(nfa, nfa_start, nfa_accept)
            output_path = "dfa.mmd"
            output_dot_path = "dfa.dot"
            write_nfa_and_dfa_mermaid(nfa, nfa_start, nfa_accept, dfa_transitions, dfa_accepting, output_path)
            write_nfa_and_dfa_dot(nfa, nfa_start, nfa_accept, dfa_transitions, dfa_accepting, output_dot_path)
            print(f"NFA and DFA diagrams written to {output_path}")
            print(f"NFA and DFA Graphviz written to {output_dot_path}")
    else:
        print("Execution canceled.")