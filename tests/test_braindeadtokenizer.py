#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120


class TestBrainDeadTokenizer(unittest.TestCase):

    def setUp(self):
        self.__tokenizer = in3120.BrainDeadTokenizer()

    def test_strings(self):
        result = list(self.__tokenizer.strings("Dette  er en\nprøve!"))
        self.assertListEqual(result, ["Dette", "er", "en", "prøve"])

    def test_tokens(self):
        result = list(self.__tokenizer.tokens("Dette  er en\nprøve!"))
        self.assertListEqual(result, [("Dette", (0, 5)), ("er", (7, 9)), ("en", (10, 12)), ("prøve", (13, 18))])

    def test_ranges(self):
        result = list(self.__tokenizer.ranges("Dette  er en\nprøve!"))
        self.assertListEqual(result, [(0, 5), (7, 9), (10, 12), (13, 18)])

    def test_empty_input(self):
        self.assertListEqual(list(self.__tokenizer.strings("")), [])
        self.assertListEqual(list(self.__tokenizer.tokens("")), [])
        self.assertListEqual(list(self.__tokenizer.ranges("")), [])

    def test_uses_yield(self):
        from types import GeneratorType
        for i in range(0, 5):
            text = "foo " * i
            self.assertIsInstance(self.__tokenizer.ranges(text), GeneratorType)
            self.assertIsInstance(self.__tokenizer.tokens(text), GeneratorType)
            self.assertIsInstance(self.__tokenizer.strings(text), GeneratorType)


if __name__ == '__main__':
    unittest.main(verbosity=2)
