#!/usr/bin/python
# -*- coding: utf-8 -*-

from .tokenizer import Tokenizer
from .trie import Trie
from typing import Iterator, Dict, Any, List, Tuple


class StringFinder:
    """
    Given a trie encoding a dictionary of strings, efficiently finds the subset of strings in the dictionary
    that are also present in a given text buffer. I.e., in a sense computes the "intersection" or "overlap"
    between the dictionary and the text buffer.

    Uses a trie-walk algorithm similar to the Aho-Corasick algorithm with some simplifications and some minor
    NLP extensions. The running time of this algorithm is virtually independent of the size of the dictionary,
    and linear in the length of the buffer we are searching in.

    The tokenizer we use when scanning the input buffer is assumed to be the same as the one that was used
    when adding strings to the trie.
    """

    def __init__(self, trie: Trie, tokenizer: Tokenizer):
        self.__trie = trie
        self.__tokenizer = tokenizer

    def scan(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Scans the given buffer and finds all dictionary entries in the trie that are also present in the
        buffer. We only consider matches that begin and end on token boundaries.

        The matching dictionary entries, if any, are yielded back to the client as dictionaries having the
        keys "match" (str) and "range" (Tuple[int, int]).

        In a serious application we'd add more lookup/evaluation features, e.g., support for prefix matching,
        support for leftmost-longest matching (instead of reporting all matches), and support for lemmatization
        or similar linguistic variations.
        """
        # The set of currently explored states. We represent a state as a node in the trie (that
        # represents where in the trie we are after having consumed zero or more characters) plus
        # an index (that represents the position into the original buffer where the state was "born".)
        # The trie node is what we advance along the way, while the index is needed so that we know where
        # we first started if/when a match is found.
        live_states : List[Tuple[Trie, int]] = []

        # Where did the previous token end? Assume that tokens are produced sorted in left-to-right
        # order.
        previous_end = -1

        # Only consider matches that start on token boundaries.
        for (string, (begin, end)) in self.__tokenizer.tokens(buffer):

            # Inject a space for the currently live states? Some languages, e.g., Japanese
            # or Chinese, don't use whitespace between tokens.
            is_juxtaposed, previous_end = (previous_end > 0) and (begin == previous_end), end
            if not is_juxtaposed:
                live_states = [(s.consume(" "), b) for (s, b) in live_states]

            # Consider this token a potential start for a match. Advance all
            # currently live states. Then prune, since consuming more characters has
            # probably killed off some states.
            live_states.append((self.__trie, begin))
            live_states = [(s.consume(string), b) for (s, b) in live_states if s]
            live_states = [(s, b) for (s, b) in live_states if s]

            # Report matches, if any, that end on the token we just consumed. Use the
            # tokenizer to somewhat normalize the matches we emit.
            for match_begin in (b for (s, b) in live_states if s.is_final()):
                yield {"match": " ".join(self.__tokenizer.strings(buffer[match_begin:end])),
                       "range": (match_begin, end)}
