from . import Regex
from .DFA import DFA
from .NFA import NFA

ERROR_CODE = -1
REACHED_FINAL_STATE = 0
REACHED_SINK_STATE = 1
REACHED_NON_FINAL_STATE = 2

class Lexer:

    dfa: DFA[int]
    nfa: NFA[int]
    l: list[tuple[set[int], str]] # (set_of_final_states, token_matched)

    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)

        # creating the final NFA and adding the initial state that will have EPSILON transitions to all other NFAs initial states
        final_nfa = NFA(set(), {0}, 0, dict(), set())
        self.l = []

        # construct each partial NFA, then remap and integrate it into the
        for (token_name, regex) in spec:
            # transform from regex to NFA using stage 2 method
            partial_nfa = Regex.parse_regex(regex).thompson()
            remapped_partial_nfa = partial_nfa.remap_states(lambda x: x + len(final_nfa.K))

            final_nfa.K.update(remapped_partial_nfa.K)
            final_nfa.S.update(remapped_partial_nfa.S)
            final_nfa.d.update(remapped_partial_nfa.d)
            final_nfa.F.update(remapped_partial_nfa.F)

            # add EPSIOLON transition to initial state
            if (0, '') in final_nfa.d:
                final_nfa.d[(0, '')].add(remapped_partial_nfa.q0)
            else:
                final_nfa.d[(0, '')] = {remapped_partial_nfa.q0}

            self.l.append((remapped_partial_nfa.F, token_name))

        self.nfa = final_nfa
        self.dfa = final_nfa.subset_construction()

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)

        final_list = []
        index = 0
        current_word = word[0]
        configuration = ("", -1, "") # (token_name, index_where_it_ends, lexeme)
        while True:
            (code, last_state) = self.dfa.lex_accept(current_word)
            if code == ERROR_CODE:
                (line, character) = find_line(word, index)
                print("ERROR. REACHED A CHARACTER THAT ISN'T IN THE ALPHABET.")
                final_list = [("", f"No viable alternative at character {character}, line {line}")]
                return final_list
            elif code == REACHED_SINK_STATE:
                # no need to go any further. stop and go back to the nearest accepted configuration
                if configuration == ("", -1, ""):
                    print("ERROR. REACHED SINK STATE")
                    (line, character) = find_line(word, index)
                    final_list = [("", f'No viable alternative at character {character}, line {line}')]
                    return final_list
                else:
                    # add last config to list and continue analyzing from that position
                    final_list.append((configuration[0], configuration[2]))
                    index = configuration[1]
                    # reset current configuration
                    current_word = ""
                    configuration = ("", -1, "")
            elif code == REACHED_NON_FINAL_STATE:
                # go further
                pass
            elif code == REACHED_FINAL_STATE:
                # update the current best configuration
                # from all the tokens that match this current word, i need to find the token which appears first in the specification
                smallest_final_state = 9999
                for state in last_state:
                    if state in self.nfa.F:
                        if state < smallest_final_state:
                            smallest_final_state = state

                # find the token_name matching this lexeme
                for i in range (0, len(self.l)):
                    if smallest_final_state in self.l[i][0]:
                        configuration = (self.l[i][1], index, current_word)
                        break

            index += 1
            # check if we reached the end of the word
            if index >= len(word):
                # if we reached EOF without previously finding a valid configration, then we have an error
                if configuration == ("", -1, ""):
                    print("ERROR. REACHED EOF.")
                    (line, character) = find_line(word, index)
                    final_list = [("", f'No viable alternative at character EOF, line {line}')]
                    return final_list
                # if we reached EOF and we previously found a valid configuration, then add it to the list and continue searching from that index
                else:
                    final_list.append((configuration[0], configuration[2]))
                    index = configuration[1] + 1
                    if index >= len(word):
                        return final_list
                    current_word = word[index]
                    configuration = ("", -1, "")
            else :
                current_word = current_word + word[index]

def find_line(word: str, index: int) -> (int, int):
    character = 0
    line = 0

    for i in range(0, index):
        if (word[i] == '\n'):
            line += 1
            character = 0
        else:
            character += 1

    return  (line, character)
