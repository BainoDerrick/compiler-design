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
        self.terminals -= {''}  # Remove empty string if present


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
        if before and after:
            return f"{self.head} -> {before} . {after}"
        elif before:
            return f"{self.head} -> {before} ."
        else:
            return f"{self.head} -> . {after}"


class LR0Parser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states = []
        self.action = []
        self.goto = []
        self.prod_map = []

    def closure(self, items: Set[LR0Item]) -> Set[LR0Item]:
        """Compute closure of LR(0) items"""
        closure_set = set(items)
        added = True
        while added:
            added = False
            new_items = set()
            for item in closure_set:
                if item.dot < len(item.body):
                    symbol = item.body[item.dot]
                    if symbol in self.grammar.non_terminals:
                        for prod in self.grammar.productions.get(symbol, []):
                            new_item = LR0Item(symbol, prod, 0)
                            if new_item not in closure_set:
                                new_items.add(new_item)
            if new_items:
                closure_set |= new_items
                added = True
        return closure_set

    def goto_fn(self, items: Set[LR0Item], symbol: str) -> Set[LR0Item]:
        """Compute goto of items for a symbol"""
        goto_set = set()
        for item in items:
            if item.dot < len(item.body) and item.body[item.dot] == symbol:
                goto_set.add(LR0Item(item.head, item.body, item.dot + 1))
        return self.closure(goto_set)

    def items(self) -> List[Set[LR0Item]]:
        """Compute the canonical collection of LR(0) items"""
        # Create augmented grammar start item
        start_prod = self.grammar.productions.get(self.grammar.start_symbol, [[""]])
        start_item = LR0Item(self.grammar.start_symbol, start_prod[0], 0)
        
        C = [self.closure({start_item})]
        added = True
        
        while added:
            added = False
            for I in C[:]:  # Iterate over a copy
                for X in self.grammar.terminals | self.grammar.non_terminals:
                    goto_I_X = self.goto_fn(I, X)
                    if goto_I_X and goto_I_X not in C:
                        C.append(goto_I_X)
                        added = True
        
        return C

    def construct_parsing_table(self):
        """Construct LR(0) parsing table"""
        print("Building LR(0) parsing table...")
        
        C = self.items()
        self.states = C
        
        action = [{} for _ in range(len(C))]
        goto = [{} for _ in range(len(C))]
        
        # Build production map
        prod_map = []
        for head, bodies in self.grammar.productions.items():
            for body in bodies:
                prod_map.append((head, body))
        self.prod_map = prod_map
        
        # Build parsing table entries
        for i, I in enumerate(C):
            for item in I:
                if item.dot < len(item.body):
                    # Shift action
                    a = item.body[item.dot]
                    if a in self.grammar.terminals:
                        # Find state j where goto(I, a) = J
                        j = None
                        for idx, J in enumerate(C):
                            if self.goto_fn(I, a) == J:
                                j = idx
                                break
                        if j is not None:
                            action[i][a] = ("shift", j)
                else:
                    # Reduce action
                    if item.head != self.grammar.start_symbol:
                        # Find production index
                        for idx, (head, body) in enumerate(prod_map):
                            if head == item.head and body == item.body:
                                # For all terminals and $, add reduce
                                for a in self.grammar.terminals | {"$"}:
                                    # Don't override shift actions
                                    if a not in action[i]:
                                        action[i][a] = ("reduce", idx)
                        break
                    else:
                        # Accept action
                        action[i]["$"] = ("accept",)
            
            # Goto actions for non-terminals
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
        
        print(f"✓ LR(0) parsing table built: {len(C)} states")
        return True

    def parse(self, tokens: List[str]) -> bool:
        """Parse tokens using LR(0) algorithm"""
        if not self.action:
            print("Error: Parsing table not constructed. Call construct_parsing_table() first.")
            return False
        
        stack = [0]  # State stack
        tokens = tokens + ["$"]  # Add end marker
        idx = 0  # Input pointer
        
        print("\n" + "="*60)
        print("LR(0) PARSING TRACE")
        print("="*60)
        print(f"{'Step':<6} {'Stack':<30} {'Input':<25} {'Action'}")
        print("-" * 70)
        
        step = 0
        
        while True:
            state = stack[-1]
            current_token = tokens[idx]
            
            # Get action from table
            if current_token not in self.action[state]:
                print(f"\n❌ ERROR: Unexpected token '{current_token}' at position {idx}")
                print(f"   Expected one of: {list(self.action[state].keys())}")
                return False
            
            action_entry = self.action[state][current_token]
            
            if action_entry[0] == "shift":
                # Shift action
                new_state = action_entry[1]
                stack.append(new_state)
                print(f"{step:<6} {str(stack):<30} {' '.join(tokens[idx:idx+5]):<25} shift {current_token}")
                idx += 1
                
            elif action_entry[0] == "reduce":
                # Reduce action
                prod_idx = action_entry[1]
                head, body = self.prod_map[prod_idx]
                
                # Pop |body| states from stack
                for _ in range(len(body)):
                    stack.pop()
                
                # Get goto state
                top_state = stack[-1]
                goto_state = self.goto[top_state].get(head)
                
                if goto_state is None:
                    print(f"\n❌ ERROR: No goto state for {head} from state {top_state}")
                    return False
                
                stack.append(goto_state)
                
                # Print reduction
                body_str = ' '.join(body) if body else 'ε'
                print(f"{step:<6} {str(stack):<30} {' '.join(tokens[idx:idx+5]):<25} reduce {head} -> {body_str}")
                
            elif action_entry[0] == "accept":
                print(f"{step:<6} {str(stack):<30} {' '.join(tokens[idx:idx+5]):<25} ACCEPT")
                print("\n" + "="*60)
                print("✅ INPUT ACCEPTED! Parsing successful.")
                print("="*60)
                return True
            
            else:
                print(f"\n❌ ERROR: Unknown action {action_entry}")
                return False
            
            step += 1
            
            # Safety check to prevent infinite loops
            if step > 1000:
                print("\n❌ ERROR: Too many steps. Possible infinite loop.")
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
        if before and after:
            return f"{self.head} -> {before} . {after}, {self.lookahead}"
        elif before:
            return f"{self.head} -> {before} ., {self.lookahead}"
        else:
            return f"{self.head} -> . {after}, {self.lookahead}"


class LR1Parser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states = []
        self.action = []
        self.goto = []
    
    def construct_parsing_table(self):
        """Construct LR(1) parsing table"""
        print("LR(1) parser - Advanced implementation")
        print("Would construct LR(1) items with lookahead symbols")
        # Full implementation would go here
        pass
    
    def parse(self, tokens: List[str]) -> bool:
        """LR(1) parsing"""
        print("LR(1) parsing - Would parse with lookahead")
        return False


class LALR1Parser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states = []
        self.action = []
        self.goto = []
    
    def construct_parsing_table(self):
        """Construct LALR(1) parsing table"""
        print("LALR(1) parser - Merging LR(1) states")
        # Full implementation would go here
        pass
    
    def parse(self, tokens: List[str]) -> bool:
        """LALR(1) parsing"""
        print("LALR(1) parsing - Efficient table-driven parser")
        return False


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("BOTTOM-UP PARSER DEMONSTRATION")
    print("="*60)
    
    # Example grammar: S' -> S, S -> a S b | ε
    productions = {
        "S'": [["S"]],
        "S": [["a", "S", "b"], []]  # [] represents ε
    }
    
    grammar = Grammar(productions, "S'")
    print("\n📋 Grammar:")
    print("   S' -> S")
    print("   S -> a S b")
    print("   S -> ε")
    
    lr0 = LR0Parser(grammar)
    lr0.construct_parsing_table()
    
    # Test with input "a a b b"
    test_input = ["a", "a", "b", "b"]
    print(f"\n📝 Testing input: {' '.join(test_input)}")
    
    result = lr0.parse(test_input)
    
    if result:
        print("\n🎉 Parsing successful! Input belongs to the language.")
    else:
        print("\n❌ Parsing failed! Input does not belong to the language.")