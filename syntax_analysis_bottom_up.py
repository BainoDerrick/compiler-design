"""
Implementing bottom-up syntax analysis algorithms: LR(0), LR(1), and LALR(1) parsers with shift-reduce logic.
"""

from collections import defaultdict, deque
from typing import List, Dict, Tuple, Set, Any


class Grammar:
    def __init__(self, productions: Dict[str, List[List[str]]], start_symbol: str):
        self.productions = productions  # {head: [[body], ...], ...}
        self.start_symbol = start_symbol
        self.terminals = set()
        self.non_terminals = set(productions.keys())
        for bodies in productions.values():
            for body in bodies:
                for symbol in body:
                    if symbol not in self.non_terminals:
                        self.terminals.add(symbol)
                        self.terminals -= {''}


class LR0Item:
    def __init__(self, head: str, body: List[str], dot: int):
        self.head = head
        self.body = body
        self.dot = dot

    def __eq__(self, other):
        return (self.head, tuple(self.body), self.dot) == (other.head, tuple(other.body), other.dot)

    def __hash__(self):
        return hash((self.head, tuple(self.body), self.dot))

    def __repr__(self):
        before = ' '.join(self.body[:self.dot])
        after = ' '.join(self.body[self.dot:])
        return f"{self.head} -> {before} . {after}"


class LRParser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states = []
        self.action = []
        self.goto = []

    def closure(self, items: Set[LR0Item]) -> Set[LR0Item]:
        closure_set = set(items)
        added = True
        while added:
            added = False
            new_items = set()
            for item in closure_set:
                if item.dot < len(item.body):
                    symbol = item.body[item.dot]
                    if symbol in self.grammar.non_terminals:
                        for prod in self.grammar.productions[symbol]:
                            new_item = LR0Item(symbol, prod, 0)
                            if new_item not in closure_set:
                                new_items.add(new_item)
                                if new_items:
                                    closure_set |= new_items
                                    added = True
        return closure_set

    def goto_fn(self, items: Set[LR0Item], symbol: str) -> Set[LR0Item]:
        goto_set = set()
        for item in items:
            if item.dot < len(item.body) and item.body[item.dot] == symbol:
                goto_set.add(LR0Item(item.head, item.body, item.dot + 1))
                return self.closure(goto_set)

            def items(self) -> List[Set[LR0Item]]:
                start_item = LR0Item(
                    self.grammar.start_symbol, self.grammar.productions[self.grammar.start_symbol][0], 0)
                C = [self.closure({start_item})]
                added = True
                while added:
                    added = False
                    for I in C[:]:
                        for X in self.grammar.terminals | self.grammar.non_terminals:
                            goto_I_X = self.goto_fn(I, X)
                            if goto_I_X and goto_I_X not in C:
                                C.append(goto_I_X)
                                added = True
                                return C
    def construct_parsing_table(self):
        # To be implemented in subclasses
        pass
    def parse(self, tokens: List[str]) -> bool:
    # To be implemented in subclasses
        pass


class LR0Parser(LRParser):

    def construct_parsing_table(self):
    # Very basic LR(0) parsing table for demonstration
        C = self.items()
        self.states = C
        action = [{} for _ in range(len(C))]
        goto = [{} for _ in range(len(C))]
        prod_map = []
        for head, bodies in self.grammar.productions.items():
            for body in bodies:
                prod_map.append((head, body))
                for i, I in enumerate(C):
                    for item in I:
                        if item.dot < len(item.body):
                            a = item.body[item.dot]
                            if a in self.grammar.terminals:
                                j = None
                                for idx, J in enumerate(C):
                                    if self.goto_fn(I, a) == J:
                                        j = idx
                                        break
                                        if j is not None:
                                            action[i][a] = ("shift", j)
                                        else:
                                            if item.head != self.grammar.start_symbol:
                                                prod_idx = prod_map.index((item.head, item.body))
                                                for a in self.grammar.terminals | {"$"}:
                                                    action[i][a] = ("reduce", prod_idx)
                                                else:
                                                    action[i]["$"] = ("accept",)
                                                    for A in self.grammar.non_terminals:
                                                        j = None
                                                        for idx, J in enumerate(C):
                                                            if self.goto_fn(I, A) == J:
                                                                j = idx
                                                                break
                                                            if j is not None:
                                                                goto[i][A] = j
                                                                self.action = action
                                                                self.goto = goto
                                                                self.prod_map = prod_map
        def parse(self, tokens: List[str]) -> bool:
            stack = [0]
            tokens = tokens + ["$"]
            idx = 0
            while True:
                state = stack[-1]
                a = tokens[idx]
                act = self.action[state].get(a)
                if act is None:
                    print(f"Error: Unexpected token '{a}' at position {idx}")
                    return False
                if act[0] == "shift":
                    stack.append(act[1])
                    idx += 1
                    print(f"Shift '{a}', stack: {stack}")
                elif act[0] == "reduce":
                    head, body = self.prod_map[act[1]]
                    for _ in body:
                        stack.pop()
                        state = stack[-1]
                        stack.append(self.goto[state][head])
                        print(f"Reduce by {head} -> {' '.join(body) if body else 'ε'}, stack: {stack}")
                elif act[0] == "accept":
                    print("Input accepted!")
                    return True
                else:
                    print("Unknown action.")
                    return False


class LR1Item(LR0Item):
    def __init__(self, head: str, body: List[str], dot: int, lookahead: str):
        super().__init__(head, body, dot)
        self.lookahead = lookahead
        def __eq__(self, other):
            return super().__eq__(other) and self.lookahead == other.lookahead
        def __hash__(self):
            return hash((self.head, tuple(self.body), self.dot, self.lookahead))
        def __repr__(self):
            before = ' '.join(self.body[:self.dot])
            after = ' '.join(self.body[self.dot:])
            return f"{self.head} -> {before} . {after}, {self.lookahead}"

class LR1Parser(LRParser):
    def construct_parsing_table(self):
    # Implement LR(1) parsing table construction (shift/reduce)
        pass
    def parse(self, tokens: List[str]) -> bool:
    # Implement LR(1) shift-reduce parsing
        pass

class LALR1Parser(LRParser):
    def construct_parsing_table(self):
    # Implement LALR(1) parsing table construction (shift/reduce)
        pass
    def parse(self, tokens: List[str]) -> bool:
    # Implement LALR(1) shift-reduce parsing
        pass
# Example usage (to be replaced with actual grammar and tokens):
if __name__ == "__main__":
# Example grammar: S' -> S, S -> a S b | ε
    productions = {
            "S'": [["S"]],
            "S": [["a", "S", "b"], []] # [] represents ε
            }
    grammar = Grammar(productions, "S'")
    lr0 = LR0Parser(grammar)
    lr0.construct_parsing_table()
    print("LR(0) Parsing Trace for input: a a b b")
    result = lr0.parse(["a", "a", "b", "b"])
    print("Accepted" if result else "Rejected")
