import fileinput
import sys

# usage: python matcher.py REGEXP FILE
# REGEXP must be quoted since we may use | as an operator
# regular expressions are reverse polish notation with
#   | alternation
#   . concatenation
#   * kleene star
# with no possibility for escaping
#
# example usage:
#   python matcher.py "da.t.a.in.n.b.r.u.d.d.sp.r.å.k.|." no.txt
#   python matcher.py " 1.0.0*. ." no.txt
#   echo "hello cat baab dog hello" | python matcher.py "he.l.l.o.ba*.b.|"
# grep equivalents:
#   grep --line-number "data\(innbrudd\|språk\)" no.txt
#   grep --line-number " 100* " no.txt
#   echo "hello cat baab dog hello" | grep --line-number "hello\|ba*b"
#
# can also use the empty string ε:
#   echo "hello cat baab dog hello" | python matcher.py "he.l.ε.l.o.bε.a*.b.|"
#   python matcher.py "da.t.a.εma.s.k.i.n.e.r.|. ." no.txt

class NFA:
    def __init__(self, initial, accepting):
        # convenient to only have one accepting state per NFA
        self.initial = initial
        self.accepting = accepting

class State:
    def __init__(self, accept):
        self.accept = accept

        # for not adding duplicates in lists, see add and match functions
        self.last_list = 0

        # the start index on the substring we are potentially matching on
        self.start = 0

        # in a general NFA states may have a lot of out edges,
        # but in our construction from regular expressions, we only need two
        self.outa = None # on form (char, State), or None
        self.outb = None # on form (char, State), or None

def generate_nfa_char(c):
    initial = State(False)
    accepting = State(True)
    initial.outa = (c, accepting)
    return NFA(initial, accepting)

def generate_nfa_split(a, b):
    initial = State(False)
    accepting = State(True)
    initial.outa = ('ε', a.initial)
    initial.outb = ('ε', b.initial)
    a.accepting.outa = ('ε', accepting)
    b.accepting.outa = ('ε', accepting)
    a.accepting.accept = False
    b.accepting.accept = False
    return NFA(initial, accepting)

def generate_nfa_concat(a, b):
    a.accepting.outa = ('ε', b.initial)
    a.accepting.accept = False
    return NFA(a.initial, b.accepting)

def generate_nfa_star(a):
    initial = State(False)
    accepting = State(True)
    initial.outa = ('ε', a.initial)
    initial.outb = ('ε', accepting)
    a.accepting.outa = ('ε', a.initial)
    a.accepting.outb = ('ε', accepting)
    a.accepting.accept = False
    return NFA(initial, accepting)

# its more efficient if we do this with fragments of NFAs instead of
# entire NFAs all the time, see https://swtch.com/~rsc/regexp/regexp1.html
# we follow construction as in slides as i think it is simpler conceptually
def generate_nfa(regexp):
    stack = []
    for c in regexp:
        if c == '|':
            b = stack.pop()
            a = stack.pop()
            stack.append(generate_nfa_split(a, b))
        elif c == '.':
            b = stack.pop()
            a = stack.pop()
            stack.append(generate_nfa_concat(a, b))
        elif c == '*':
            stack.append(generate_nfa_star(stack.pop()))
        else:
            stack.append(generate_nfa_char(c))

    return stack.pop()

def add_if_label_match(out, c, start, new_states, list_id):
    if out:
        (label, state) = out
        if label == c:
            add(new_states, state, start, list_id)

def add(new_states, state, start, list_id):
    if state.last_list == list_id:
        return

    state.last_list = list_id
    state.start = start
    new_states.append(state)
    # handle ε-transitions, aka add epsilon closure
    add_if_label_match(state.outa, 'ε', start, new_states, list_id)
    add_if_label_match(state.outb, 'ε', start, new_states, list_id)

def step(c, states, new_states, list_id):
    for state in states:
        add_if_label_match(state.outa, c, state.start, new_states, list_id)
        add_if_label_match(state.outb, c, state.start, new_states, list_id)

def match(s, nfa, char_set):
    list_id = 0
    states = []
    matches = []
    for i in range(len(s)):
        list_id += 1
        # optimization but not needed: if character not in regexp alphabet,
        # avoid running step function and just reset states manually.
        # typically gives > 2x time performance
        if s[i] not in char_set:
            states = []
            continue

        nfa.initial.start = i
        add(states, nfa.initial, i, list_id)
        new_states = []
        step(s[i], states, new_states, list_id)
        states = new_states
        if nfa.accepting in states:
            matches.append((nfa.accepting.start, i + 1))
            # reset states to avoid overlapping matches
            states = []

    return matches

def print_matches(matches, line, line_nr, colours):
    sys.stdout.write(colours.GREEN + str(line_nr))
    sys.stdout.write(colours.BLUE + ':' + colours.ENDC)
    k = 0
    for (i, j) in matches:
        sys.stdout.write(line[k:i])
        sys.stdout.write(colours.RED + line[i:j] + colours.ENDC)
        k = j

    sys.stdout.write(line[k:])

if __name__ == '__main__':
    regexp = sys.argv[1]
    fs = sys.argv[2:]
    nfa = generate_nfa(regexp)
    # char_set not needed but small optimization, see match function
    char_set = {c for c in regexp if c not in '|.*'}

    # only colour output if written to terminal
    isatty = sys.stdout.isatty()
    class colours:
        RED = '\033[31m' if isatty else ''
        GREEN = '\033[32m' if isatty else ''
        BLUE = '\033[34m' if isatty else ''
        ENDC = '\033[m' if isatty else ''

    line_nr = 1
    for line in fileinput.input(files=fs):
        matches = match(line, nfa, char_set)
        if matches:
            print_matches(matches, line, line_nr, colours)

        line_nr += 1
