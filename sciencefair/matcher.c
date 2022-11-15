/*
 * Regular expression implementation.
 * Supports only ( | ) * + ?.  No escapes.
 * Compiles to NFA and then simulates NFA
 * using Thompson's algorithm.
 *
 * See also http://swtch.com/~rsc/regexp/ and
 * Thompson, Ken.  Regular Expression Search Algorithm,
 * Communications of the ACM 11(6) (June 1968), pp. 419-422.
 *
 * Copyright (c) 2007 Russ Cox.
 * Can be distributed under the MIT license, see bottom of file.
 */

// modified by E nov 2022, all comments starting with // are mine
// original program was to see if a regular expression matches a string,
// modified to search for matching substrings in larger text/file
// original src file: https://swtch.com/~rsc/regexp/nfa.c.txt
// as the code is mostly for educational purposes, russ didnt care about
// memory leaks etc, so neither do i (although there are only few)
//
// compile with optization: cc -O3 matcher.c -o matcher
//
// example usage:
//   ./matcher "data(innbrudd|språk)" no.txt
//   ./matcher " 100* " no.txt
//   echo "hello cat baab dog hello" | ./matcher "hello|ba*b"
// grep equivalents:
//   grep --line-number "data\(innbrudd\|språk\)" no.txt
//   grep --line-number " 100* " no.txt
//   echo "hello cat baab dog hello" | grep --line-number "hello\|ba*b"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/*
 * Convert infix regexp re to postfix notation.
 * Insert . as explicit concatenation operator.
 * Cheesy parser, return static buffer.
 */
char*
re2post(char *re)
{
	int nalt, natom;
	static char buf[8000];
	char *dst;
	struct {
		int nalt;
		int natom;
	} paren[100], *p;

	p = paren;
	dst = buf;
	nalt = 0;
	natom = 0;
	if(strlen(re) >= sizeof buf/2)
		return NULL;
	for(; *re; re++){
		switch(*re){
		case '(':
			if(natom > 1){
				--natom;
				*dst++ = '.';
			}
			if(p >= paren+100)
				return NULL;
			p->nalt = nalt;
			p->natom = natom;
			p++;
			nalt = 0;
			natom = 0;
			break;
		case '|':
			if(natom == 0)
				return NULL;
			while(--natom > 0)
				*dst++ = '.';
			nalt++;
			break;
		case ')':
			if(p == paren)
				return NULL;
			if(natom == 0)
				return NULL;
			while(--natom > 0)
				*dst++ = '.';
			for(; nalt > 0; nalt--)
				*dst++ = '|';
			--p;
			nalt = p->nalt;
			natom = p->natom;
			natom++;
			break;
		case '*':
		case '+':
		case '?':
			if(natom == 0)
				return NULL;
			*dst++ = *re;
			break;
		default:
			if(natom > 1){
				--natom;
				*dst++ = '.';
			}
			*dst++ = *re;
			natom++;
			break;
		}
	}
	if(p != paren)
		return NULL;
	while(--natom > 0)
		*dst++ = '.';
	for(; nalt > 0; nalt--)
		*dst++ = '|';
	*dst = 0;
	return buf;
}

/*
 * Represents an NFA state plus zero or one or two arrows exiting.
 * if c == Match, no arrows out; matching state.
 * If c == Split, unlabeled arrows to out and out1 (if != NULL).
 * If c < 256, labeled arrow with character c to out.
 */
enum
{
	Match = 256,
	Split = 257
};
typedef struct State State;
struct State
{
	int c;
	State *out;
	State *out1;
	int lastlist;
	int start;
};
State matchstate = { Match };	/* matching state */
int nstate;

/* Allocate and initialize State */
State*
state(int c, State *out, State *out1)
{
	State *s;

	nstate++;
	s = malloc(sizeof *s);
	s->lastlist = 0;
	s->start = 0;
	s->c = c;
	s->out = out;
	s->out1 = out1;
	return s;
}

/*
 * A partially built NFA without the matching state filled in.
 * Frag.start points at the start state.
 * Frag.out is a list of places that need to be set to the
 * next state for this fragment.
 */
typedef struct Frag Frag;
typedef union Ptrlist Ptrlist;
struct Frag
{
	State *start;
	Ptrlist *out;
};

/* Initialize Frag struct. */
Frag
frag(State *start, Ptrlist *out)
{
	Frag n = { start, out };
	return n;
}

/*
 * Since the out pointers in the list are always
 * uninitialized, we use the pointers themselves
 * as storage for the Ptrlists.
 */
union Ptrlist
{
	Ptrlist *next;
	State *s;
};

/* Create singleton list containing just outp. */
Ptrlist*
list1(State **outp)
{
	Ptrlist *l;

	l = (Ptrlist*)outp;
	l->next = NULL;
	return l;
}

/* Patch the list of states at out to point to start. */
void
patch(Ptrlist *l, State *s)
{
	Ptrlist *next;

	for(; l; l=next){
		next = l->next;
		l->s = s;
	}
}

/* Join the two lists l1 and l2, returning the combination. */
Ptrlist*
append(Ptrlist *l1, Ptrlist *l2)
{
	Ptrlist *oldl1;

	oldl1 = l1;
	while(l1->next)
		l1 = l1->next;
	l1->next = l2;
	return oldl1;
}

/*
 * Convert postfix regular expression to NFA.
 * Return start state.
 */
State*
post2nfa(char *postfix)
{
	char *p;
	Frag stack[1000], *stackp, e1, e2, e;
	State *s;

	// fprintf(stderr, "postfix: %s\n", postfix);

	if(postfix == NULL)
		return NULL;

	#define push(s) *stackp++ = s
	#define pop() *--stackp

	stackp = stack;
	for(p=postfix; *p; p++){
		switch(*p){
		default:
			s = state(*p, NULL, NULL);
			push(frag(s, list1(&s->out)));
			break;
		case '.':	/* catenate */
			e2 = pop();
			e1 = pop();
			patch(e1.out, e2.start);
			push(frag(e1.start, e2.out));
			break;
		case '|':	/* alternate */
			e2 = pop();
			e1 = pop();
			s = state(Split, e1.start, e2.start);
			push(frag(s, append(e1.out, e2.out)));
			break;
		case '?':	/* zero or one */
			e = pop();
			s = state(Split, e.start, NULL);
			push(frag(s, append(e.out, list1(&s->out1))));
			break;
		case '*':	/* zero or more */
			e = pop();
			s = state(Split, e.start, NULL);
			patch(e.out, s);
			push(frag(s, list1(&s->out1)));
			break;
		case '+':	/* one or more */
			e = pop();
			s = state(Split, e.start, NULL);
			patch(e.out, s);
			push(frag(e.start, list1(&s->out1)));
			break;
		}
	}

	e = pop();
	if(stackp != stack)
		return NULL;

	patch(e.out, &matchstate);
	return e.start;
#undef pop
#undef push
}

typedef struct List List;
struct List
{
	State **s;
	int n;
};
List l1, l2;
static int listid;

void addstate(List*, State*, int);
void step(List*, State*, int, int, List*);

/* Compute initial state list */
List*
startlist(State *start, List *l)
{
	l->n = 0;
	listid++;
	addstate(l, start, 0);
	return l;
}

/* Check whether state list contains a match. */
// int
// ismatch(List *l)
// {
// 	int i;
//
// 	for(i=0; i<l->n; i++)
// 		if(l->s[i] == &matchstate)
// 			return 1;
// 	return 0;
// }
// dont need this: instead check if matchstate.lastlist == listid

/* Add s to l, following unlabeled arrows. */
void
addstate(List *l, State *s, int start)
{
	if(s == NULL || s->lastlist == listid)
		return;
	s->lastlist = listid;
	s->start = start;
	if(s->c == Split){
		/* follow unlabeled arrows */
		addstate(l, s->out, start);
		addstate(l, s->out1, start);
		return;
	}
	l->s[l->n++] = s;
}

/*
 * Step the NFA from the states in clist
 * past the character c,
 * to create next NFA state set nlist.
 */
void
step(List *clist, State *start, int c, int j, List *nlist)
{
	int i;
	State *s;

	addstate(clist, start, j);
	listid++;
	nlist->n = 0;
	for(i=0; i<clist->n; i++){
		s = clist->s[i];
		if(s->c == c)
			addstate(nlist, s->out, s->start);
	}
}

// for storing info on matching substrings
typedef struct Slice Slice;
struct Slice {
	int start;
	int end;
	Slice *next;
};

void
addslice(Slice **slicep, int start, int end)
{
	for(; *slicep; slicep = &(*slicep)->next);
	*slicep = malloc(sizeof **slicep);
	(*slicep)->start = start;
	(*slicep)->end = end;
	(*slicep)->next = NULL;
}

void
match(State *start, char *s, Slice **matchesp)
{
	int i, c;
	List *clist, *nlist, *t;

	clist = startlist(start, &l1);
	nlist = &l2;
	i = 0;
	for(; s[i]; i++){
		// want to include æøå, but possibly introduces bug when
		// it comes to UTF-8 charactars where 256 (our epsilon char) occurs
		// in a byte and its following bit? idk strings are hard
		// but things seem to work as they are now
		// c = s[i] & 0xFF;
		c = s[i];
		step(clist, start, c, i, nlist);
 		t = clist; clist = nlist; nlist = t;	/* swap clist, nlist */
		// if(ismatch(clist))
		if(matchstate.lastlist == listid)
			addslice(matchesp, matchstate.start, i + 1);
	}
}

char *RED, *GREEN, *BLUE, *ENDC;

void
printmatches(Slice *matches, char *line, int linenr)
{
	Slice *slice;
	int i, j, k;

	if(matches == NULL)
		return;

	printf("%s%d%s:%s", GREEN, linenr, BLUE, ENDC);

	k = 0;
	for(slice = matches; slice; slice = slice->next){
		i = slice->start;
		j = slice->end;
		for (; k < i; k++)
			putchar(line[k]);

		fputs(RED, stdout);
		for (; k < j; k++)
			putchar(line[k]);

		fputs(ENDC, stdout);
	}

	for (; line[k]; k++)
		putchar(line[k]);
}

int
main(int argc, char **argv)
{
	char *post;
	State *start;
	int atty;
	FILE *in;
	char *line;
	int linenr;
	size_t len;
	ssize_t read;

 	if(argc < 2){
 		fprintf(stderr, "usage: nfa regexp file\n");
 		fprintf(stderr, "see source file for examples\n");
 		return 1;
 	}

	// this wont pick up all bad regexps,
	// resulting in seg fault sometimes
 	post = re2post(argv[1]);
 	if(post == NULL){
 		fprintf(stderr, "bad regexp %s\n", argv[1]);
 		fprintf(stderr, "see source file for examples\n");
 		return 1;
 	}

 	start = post2nfa(post);
 	if(start == NULL){
 		fprintf(stderr, "error in post2nfa %s\n", post);
 		return 1;
 	}

	atty = isatty(fileno(stdout));
	RED   = atty ? "\033[31m" : "";
	GREEN = atty ? "\033[32m" : "";
	BLUE  = atty ? "\033[34m" : "";
	ENDC  = atty ? "\033[m"   : "";

 	l1.s = malloc(nstate*sizeof l1.s[0]);
 	l2.s = malloc(nstate*sizeof l2.s[0]);
	line = NULL;
	len = 0;
	in = argc > 2 ? fopen(argv[2], "r") : stdin;
	for(linenr = 0; (read = getline(&line, &len, in)) != -1; linenr++){
		Slice *matches = NULL;
		match(start, line, &matches);
		printmatches(matches, line, linenr);
	}

 	return 0;
}

/*
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the
 * Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute,
 * sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall
 * be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
 * KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 * PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS
 * OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
 * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
