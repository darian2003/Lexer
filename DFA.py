from collections.abc import Callable
from dataclasses import dataclass
ERROR_CODE = -1
REACHED_FINAL_STATE = 0
REACHED_SINK_STATE = 1
REACHED_NON_FINAL_STATE = 2

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]


    def __str__(self):
        new_d = dict()
        for (key, value) in self.d.items():
            if value == frozenset():
                continue
            (state, c) = key
            if state == frozenset():
                continue
            new_d[key] = value

        return f'S={self.S} K={self.K} q0={self.q0} new_d={new_d} f={self.F}'

    def accept(self, word: str) -> bool:
        # simulate the dfa on the given word. return true if the dfa accepts the word, false otherwise
        current_state = self.q0
        while word != "":
            if word[0] not in self.S:
                return False
            current_state = frozenset(self.d[(current_state, word[0])])
            word = word[1:]
        if current_state in self.F:
            return True
        return False

    def lex_accept(self, word: str) -> (int, frozenset):
        # simulate the dfa on the given word. return 0 if the dfa accepts the word, 1 if we reach the sink state, 2 if we reach a non-final state and -1 in case of error
        current_state = self.q0
        while word != "":
            if word[0] not in self.S:
                print(f"Char {word[0]} not in alphabet")
                return (ERROR_CODE, "")
            current_state = frozenset(self.d[(current_state, word[0])])
            word = word[1:]
            if current_state == frozenset(): # check if we are in sinkstate
                return (REACHED_SINK_STATE, current_state)
        if current_state in self.F:
            return (REACHED_FINAL_STATE, current_state)
        return (REACHED_NON_FINAL_STATE, current_state)

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        new_k = set()
        new_d = dict()
        new_f = set()
        for state in self.K:
            new_k.add(f(state))
        for state in self.F:
            new_f.add(f(state))
        new_q0 = f(self.q0)
        for (state, c) in self.d:
            new_d[(f(state), c)] = f(self.d[(state, c)])

        return DFA(self.S, new_k, new_q0, new_d, new_f)


