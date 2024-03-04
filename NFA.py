from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        # see the EPSILON definition at the top of this file

        visited = {state} # orice epsilon_closure va contine obligatoriu starea din care plecam. in setul visited vom crea epsilon_closer-ul
        not_visited = set()
        if (state, EPSILON) in self.d: # verific daca am epsilon-tranzitie din starea din care plec
            not_visited = set(self.d[(state, '')])

        while not_visited: # check if queue is empty
            new_state = not_visited.pop()
            visited.add(new_state) # am visitat aceasta stare deci o adaugam la epsilon_closure
            if (new_state, EPSILON) in self.d:
                new_possible_states = self.d[(new_state, EPSILON)] # verificam daca din noua stare in care ne aflam putem extinde epsilon_closer-ul
                for state in new_possible_states:
                    if state not in visited:     # pentru a evita ciclurile, vom adauga in coada de stari nevizitate doar acele stari prin care n am mai trecut
                        not_visited.add(state)
        return visited


    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # convert this nfa to a dfa using the subset construction algorithm
        # Initializam noile date pe care le vom pasa constructorului de DFA
        dfa_k = set()
        dfa_d = dict()
        dfa_final_states = set()

        sink = frozenset()  # sink = empty-set
        dfa_k.add(sink)
        for c in self.S:
            dfa_d[(sink, c)] = sink # orice tranzitie care pleaca din sink, duce tot in sink

        dfa_q0 = frozenset(self.epsilon_closure(self.q0))           # creez starea initiala a DFA-ului din starea initiala a NFA-ului
        not_visited = {dfa_q0}      # initializez coada de seturi de stari nevizitate
        while not_visited:                      # atata timp cat inca mai am stari de vizitat
            set_of_states = not_visited.pop()
            dfa_k.add(set_of_states)            # vizitez starea => o adaug in setul de stari ale DFA-ului
            for state in set_of_states:
                if state in self.F:             # devine stare finala in DFA daca contine cel putin o stare finala de NFA in codificare
                    dfa_final_states.add(set_of_states)
                    break

            for c in self.S:       # pentru toate caracterele din alfabet
                new_set_of_states = set()       # ma pregatesc sa creez noua stare a DFA-ului
                for state in set_of_states:         # pentru fiecare stare din codificarea stariilor tip DFA = {1,2,3}
                    if (state, c) in self.d:        # daca exista in dictionarul NFA-ului o tranzitie pe caracterul c
                        for reachable_state in self.d[(state, c)]:
                            new_set_of_states.update(self.epsilon_closure(reachable_state))     # adauga epsilon closure-ul tuturor reachable state-urilor in noul set de stari
                if new_set_of_states:
                    dfa_d[(set_of_states, c)] = new_set_of_states           # adauga noua tranzitie in dictionar
                    if frozenset(new_set_of_states) not in dfa_k:           # daca nu am mai vizitat starea in care duce noua tranzitie, adaug-o in coada de stari nevizitate
                        not_visited.add(frozenset(new_set_of_states))       # daca nu am verifica aceasta conditie si ar exista cicluri in NFA, programul ar putea rula la infinit
                else:
                    dfa_d[(set_of_states, c)] = sink  # orice alta tranzitie duce in sink state

        dfa = DFA(self.S, dfa_k, dfa_q0, dfa_d, dfa_final_states)

        return dfa


    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.

        new_k = set()
        new_d = dict()
        new_f = set()
        for state in self.K:
            new_k.add(f(state))
        for state in self.F:
            new_f.add(f(state))
        new_q0 = f(self.q0)
        for (state, c) in self.d:
            new_set = set()
            for value_state in self.d[(state, c)]:
                new_set.add(f(value_state))
            new_d[f(state), c] = new_set

        return NFA(self.S, new_k, new_q0, new_d, new_f)

        pass

