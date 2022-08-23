#!/usr/bin/python
# -*- coding: utf-8 -*-

from .tokenizer import Tokenizer
from typing import Iterator, Tuple


class ShingleGenerator(Tokenizer):
    """
    Tokenizes a buffer into overlapping shingles having a specified width. For example, the
    3-shingles for "mouse" are {"mou", "ous", "use"}.
    """

    def __init__(self, width: int):
        assert width > 0
        self.__width = width

    def ranges(self, buffer: str) -> Iterator[Tuple[int, int]]:
        """
        Locates where the shingles begin and end.
        """
        raise NotImplementedError("You need to implement this as part of the assignment.")
