#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
from .tokenizer import Tokenizer
from typing import Optional, Iterable


class Trie:
    """
    A very simple and straightforward implementation of a trie for demonstration purposes
    and tiny dictionaries.

    A serious real-world implementation of a trie or an automaton would not be implemented
    this way. The trie/automaton would then instead be encoded into a single contiguous buffer
    and there'd be significant attention on memory consumption and scalability with respect to
    dictionary size.

    A node in the trie is also a trie itself in this implementation.
    """

    def __init__(self):
        self.__children = {}

    def __repr__(self):
        return repr(self.__children)

    def __add(self, string: str) -> None:
        assert 0 < len(string)
        trie = self
        for c in string:
            if c not in trie.__children:
                trie.__children[c] = Trie()
            trie = trie.__children[c]
        trie.__children[""] = Trie()

    def add(self, strings: Iterable[str], tokenizer: Tokenizer) -> None:
        """
        Adds all the strings to the trie. The tokenizer is used so that we're robust
        to nuances in whitespace and punctuation. Use the same tokenizer throughout.
        """
        # TODO: Make the tokenizer a class variable.
        for string in strings:
            self.__add(" ".join(tokenizer.strings(string)))

    def consume(self, prefix: str) -> Optional[Trie]:
        """
        Consumes the given prefix, verbatim. If strings that have this prefix have been added to
        the trie, then the trie node corresponding to the prefix is returned. Otherwise, None is returned.
        """
        trie = self
        for c in prefix:
            if c in trie.__children:
                trie = trie.__children[c]
            else:
                return None
        return trie

    def is_final(self) -> bool:
        """
        Returns True iff the current node is a final/terminal state in the trie/automaton, i.e.,
        if a string has been added to the trie where the end of the string ends up in this node.
        """
        return "" in self.__children
