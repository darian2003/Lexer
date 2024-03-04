from dataclasses import dataclass
import string

from .NFA import NFA


class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('the thompson method of the Regex class should never be called')

# you should extend this class with the type constructors of regular expressions and overwrite the 'thompson' method
# with the specific nfa patterns. for example, parse_regex('ab').thompson() should return something like:

# >(0) --a--> (1) -epsilon-> (2) --b--> ((3))

# extra hint: you can implement each subtype of regex as a @dataclass extending Regex

@dataclass
class Epsilon(Regex):
    def thompson(self) -> NFA[int]:
        return NFA(set(), {0}, 0, {}, {0})

@dataclass
class Empty(Regex):
    def thompson(self) -> NFA[int]:
        return NFA(set(), {0, 1}, 0, {}, {1})

@dataclass
class Character(Regex):
    def __init__(self, c):
        self.char = c

    def thompson(self) -> NFA[int]:
        return NFA({self.char}, {0, 1}, 0, {(0, self.char): {1}}, {1})

@dataclass
class OpenParanthese(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({'('}, {0, 1}, 0, {(0, '('): {1}}, {1})

@dataclass
class CloseParanthese(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({')'}, {0, 1}, 0, {(0, ')'): {1}}, {1})

@dataclass
class Colon(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({':'}, {0, 1}, 0, {(0, ':'): {1}}, {1})

@dataclass
class Space(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({' '}, {0, 1}, 0, {(0, ' '): {1}}, {1})

@dataclass
class Lambda(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({'l', 'a', 'm', 'b', 'd', 'a'}, {0, 1, 2, 3, 4, 5, 6}, 0, {(0, 'l'): {1}, (1, 'a'): {2}, (2, 'm'): {3}, (3, 'b'): {4}, (4, 'd'): {5}, (5, 'a'): {6}}, {6})

@dataclass
class Sum(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({'+'}, {0, 1}, 0, {(0, '+'): {1}}, {1})

@dataclass
class Newline(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({'\n'}, {0, 1}, 0, {(0, '\n'): {1}}, {1})


@dataclass
class Tab(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({'\t'}, {0, 1}, 0, {(0, '\t'): {1}}, {1})
@dataclass
class ListConcat(Regex):

    def thompson(self) -> NFA[int]:
        return NFA({'+'}, {0, 1, 2}, 0, {(0, '+'): {1}, (1, '+'): {2}}, {2})

@dataclass
class Concat(Regex):

    left: NFA
    right: NFA

    def __init__(self, left: Regex, right: Regex):
        self.left = left.thompson()
        self.right = right.thompson()

    def f(self, initial_state):
        new_state = initial_state + len(self.left.K)
        return new_state

    def thompson(self) -> NFA[int]:
        remapped_right_thompson = self.right.remap_states(self.f) # remapez starile din NFA-ul din dreapta. Noul automat va avea stari de la 0 pana la |K1| + |K2|

        new_s = self.left.S.union(self.right.S) # reunesc alfabetele

        new_k = self.left.K.union(remapped_right_thompson.K) # reunesc starile

        new_q0 = self.left.q0 # actualizez starea initiala

        new_d = self.left.d.copy() # initializez dictionarul cu cel al NFA-ului din stanga
        new_d.update(remapped_right_thompson.d) # adaug si tranzitiile NFA-ului din dreapta

        left_final_state = self.left.F.pop()

        new_d[left_final_state, ''] = {remapped_right_thompson.q0} # adaug tranzitia care leaga cele doua NFA-uri
        new_f = remapped_right_thompson.F # starea finala noua coincide cu starea finala din dreapta

        nfa = NFA(new_s, new_k, new_q0, new_d, new_f)
        return nfa

class Union(Regex):

    up: NFA
    down: NFA

    def __init__(self, up: Regex, down: Regex):
        self.up = up.thompson()
        self.down = down.thompson()

    def f_up(self, initial_state):
        new_state = initial_state + 1
        return new_state

    def f_down(self, initial_state):
        new_state = initial_state + len(self.up.K) + 1
        return new_state

    def thompson(self) -> NFA[int]:
        remapped_up_thompson = self.up.remap_states(self.f_up) # remapez starile din NFA-ul de sus
        remapped_down_thompson = self.down.remap_states(self.f_down)  # remapez starile din NFA-ul de jos

        new_s = self.up.S.union(self.down.S)  # reunesc alfabetele

        new_k = remapped_down_thompson.K.union(remapped_up_thompson.K) # reunesc starile

        new_q0 = 0 # creez starea initiala
        new_k.add(new_q0) # adaug starea initiala la multimea de stari

        final_state = len(self.up.K) + len(self.down.K) + 1
        new_f = {final_state} # creez starea finala
        new_k.add(final_state) # adaug starea finala

        new_d = remapped_up_thompson.d.copy()  # initializez dictionarul cu cel al NFA-ului de sus
        new_d.update(remapped_down_thompson.d)  # adaug si tranzitiile NFA-ului de jos
        # adaug tranzitiile care leaga noua stare initiala de cele doua vechi stari initiale ale NFA-urilor
        new_d[new_q0, ''] = {remapped_up_thompson.q0, remapped_down_thompson.q0}
        # adaug tranzitiile care leaga vechile stari finale de noua stare finala
        new_d[remapped_down_thompson.F.pop(), ''] = {final_state}
        new_d[remapped_up_thompson.F.pop(), ''] = {final_state}

        nfa = NFA(new_s, new_k, new_q0, new_d, new_f)
        return nfa

class Star(Regex):

    starting_nfa: NFA

    def __init__(self, starting_regex: Regex):
        self.starting_nfa = starting_regex.thompson()

    def f(self, initial_state):
        new_state = initial_state + 1
        return new_state

    def thompson(self) -> NFA[int]:
        remapped_nfa = self.starting_nfa.remap_states(self.f)

        new_S = remapped_nfa.S # alfabetul ramane acelasi

        new_k = remapped_nfa.K

        new_q0 = 0
        new_k.add(new_q0)

        new_final_state = len(self.starting_nfa.K) + 1 # creez noua stare finala
        new_k.add(new_final_state) # o adaug la setul de stari
        new_f = {new_final_state}

        new_d = remapped_nfa.d
        new_d[0, ''] = {1, new_final_state} # adaug noile Epsilon tranzitii
        old_final_state = self.f(self.starting_nfa.F.pop())
        old_q0 = self.f(self.starting_nfa.q0)
        new_d[old_final_state, ''] = {old_q0, new_final_state}

        nfa = NFA(new_S, new_k, new_q0, new_d, new_f)
        return nfa

class QuestionMark(Regex):
    starting_nfa: NFA

    def __init__(self, starting_regex: Regex):
        self.starting_nfa = starting_regex.thompson()

    def f(self, initial_state):
        new_state = initial_state + 1
        return new_state

    def thompson(self) -> NFA[int]:
        remapped_nfa = self.starting_nfa.remap_states(self.f)

        new_S = remapped_nfa.S  # alfabetul ramane acelasi

        new_k = remapped_nfa.K

        new_q0 = 0
        new_k.add(new_q0)

        new_final_state = len(self.starting_nfa.K) + 1  # creez noua stare finala
        new_k.add(new_final_state)  # o adaug la setul de stari
        new_f = {new_final_state}

        new_d = remapped_nfa.d
        new_d[0, ''] = {1, new_final_state} # adaug noile Epsilon tranzitii
        old_final_state = self.f(self.starting_nfa.F.pop())
        new_d[old_final_state, ''] = {new_final_state}

        nfa = NFA(new_S, new_k, new_q0, new_d, new_f)
        return nfa

class Plus(Regex):
    starting_nfa: NFA

    def __init__(self, starting_regex: Regex):
        self.starting_nfa = starting_regex.thompson()

    def f(self, initial_state):
        new_state = initial_state + 1
        return new_state

    def thompson(self) -> NFA[int]:
        remapped_nfa = self.starting_nfa.remap_states(self.f)

        new_S = remapped_nfa.S  # alfabetul ramane acelasi

        new_k = remapped_nfa.K

        new_q0 = 0
        new_k.add(new_q0)

        new_final_state = len(self.starting_nfa.K) + 1  # creez noua stare finala
        new_k.add(new_final_state)  # o adaug la setul de stari
        new_f = {new_final_state}

        new_d = remapped_nfa.d
        new_d[0, ''] = {1}
        old_final_state = self.f(self.starting_nfa.F.pop())
        old_initial_state = self.f(self.starting_nfa.q0)
        new_d[old_final_state, ''] = {new_final_state, old_initial_state}

        nfa = NFA(new_S, new_k, new_q0, new_d, new_f)
        return nfa

@dataclass
class AnyLowerCase(Regex):

    def thompson(self) -> NFA[int]:
        k = {0, 1}
        s = set()
        d = dict()
        q0 = 0
        f = {1}
        for letter in string.ascii_lowercase:
            s.add(letter)
            d[0, letter] = {1}

        nfa = NFA(s, k, q0, d, f)

        return nfa

@dataclass
class AnyUpperCase(Regex):

    def thompson(self) -> NFA[int]:
        k = {0, 1}
        s = set()
        d = dict()
        q0 = 0
        f = {1}
        for letter in string.ascii_uppercase:
            s.add(letter)
            d[0, letter] = {1}

        nfa = NFA(s, k, q0, d, f)

        return nfa

@dataclass
class AnyDigit(Regex):

    def thompson(self) -> NFA[int]:
        k = {0, 1}
        s = set()
        d = dict()
        q0 = 0
        f = {1}
        for digit in "0123456789":
            s.add(digit)
            d[0, digit] = {1}

        nfa = NFA(s, k, q0, d, f)

        return nfa

def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string
    (final_regex, empty_string) = parse_regex_helper(regex)
    return final_regex

# Daca citim un caracter special, functia returneaza noul regex format in
# urma operatiei speciale sau returneaza acelasi regex pe care l-a primit in caz contrar
def check_special_character(remaining_regex: str, current_regex: Regex) -> (str, Regex):
    new_regex = current_regex
    if remaining_regex[0] == "*":
        new_regex = Star(current_regex)
        remaining_regex = remaining_regex[1:]
    elif remaining_regex[0] == "?":
        new_regex = QuestionMark(current_regex)
        remaining_regex = remaining_regex[1:]
    elif remaining_regex[0] == "+":
        new_regex = Plus(current_regex)
        remaining_regex = remaining_regex[1:]
    return (remaining_regex, new_regex)

# Functie ajutataoare recursiva care computeaza fragmente din regex-ul initial
def parse_regex_helper(regex: str) -> (Regex, str):
    current_regex = Epsilon()
    init = False                # voi folosi aceasta variabila pentru a verifica daca regex-ul meu este gol sau initializat
    while regex:
        match regex[0]:
            case " ":                   # ignoram spatiile
                regex = regex[1:]
            case "|":
                regex = regex[1:]       # taiem |
                if regex[0] == " ":
                    regex = regex[1:]   # taiem si spatiul de dupa |
                (parsed_regex, regex) = parse_regex_helper(regex)   # computam membrul din dreapta operatiei de Union()
                if init:
                    current_regex = Union(current_regex, parsed_regex)
                else:
                    current_regex = parsed_regex
                    init = True
                continue
            case "(":
                (parsed_regex, regex) = parse_regex_helper(regex[1:])       # computam intreaga paranteza
                if regex[0] == ')':
                    regex = regex[1:]       # citesc ")"
                    if len(regex) > 0:      # verific daca am vreun element *, +, ? dupa paranteza
                        (regex, parsed_regex) = check_special_character(regex, parsed_regex)
                if init:
                    current_regex = Concat(current_regex, parsed_regex)
                else:
                    current_regex = parsed_regex
                    init = True
            case ")":
                return (current_regex, regex)

            case "+":
                if len(regex) > 1:
                    if regex[1] == "+":
                        regex = regex[2:]
                        return ListConcat(), regex
                return Sum(), regex

            case "[":
                temp_regex = Epsilon()
                match regex[1]:
                    case "a":
                        temp_regex = AnyLowerCase()
                    case "A":
                        temp_regex = AnyUpperCase()
                    case "0":
                        temp_regex = AnyDigit()
                regex = regex[5:]       # am taiat [x-y]
                if len(regex) > 0:      # verifica daca avem vreun caracter special *+? dupa []
                    (regex, temp_regex) = check_special_character(regex, temp_regex)
                if init:
                    current_regex = Concat(current_regex, temp_regex)
                else:
                    current_regex = temp_regex
                    init = True

            case "\\":
                regex = regex[1:]
                temp_regex = Epsilon()
                if len(regex) > 0:
                    if regex[0] == "n":
                        temp_regex = Character("\n")
                    else:
                        temp_regex = Character(regex[0])
                    regex = regex[1:]
                    if len(regex) > 0:      # verifica daca avem vreun caracter special dupa
                        (regex, temp_regex) = check_special_character(regex, temp_regex)
                    if init:
                        current_regex = Concat(current_regex, temp_regex)
                    else:
                        current_regex = temp_regex
                        init = True

            case _: # orice caracter normal (a,b,c ...)
                if regex[0] == "l" :
                    if len(regex) > 6:
                        if regex[1:7] == "ambda ":
                            return Lambda(), regex[7:]
                temp_regex = Character(regex[0])
                regex = regex[1:]
                if len(regex) > 0:
                    (regex, temp_regex) = check_special_character(regex, temp_regex)
                if init:
                    current_regex = Concat(current_regex, temp_regex)
                else:
                    current_regex = temp_regex
                    init = True

    return (current_regex, regex)

    # you can define additional classes and functions to help with the parsing process

    # the checker will call this function, then the thompson method of the generated object. the resulting NFA's
    # behaviour will be checked using your implementation form stage 1

