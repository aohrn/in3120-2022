#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120


class TestStringFinder(unittest.TestCase):

    def setUp(self):
        self.__tokenizer = in3120.BrainDeadTokenizer()

    def __scan_text_verify_matches(self, finder, text, expected):
        matches = list(finder.scan(text))
        self.assertListEqual([m["match"] for m in matches], expected)

    def test_scan_matches_only(self):
        dictionary = in3120.Trie()
        dictionary.add(["romerike", "apple computer", "norsk", "norsk ørret", "sverige",
                        "ørret", "banan", "a", "a b"], self.__tokenizer)
        finder = in3120.StringFinder(dictionary, self.__tokenizer)
        self.__scan_text_verify_matches(finder,
                                        "en norsk     ørret fra romerike likte abba fra sverige",
                                        ["norsk", "norsk ørret", "ørret", "romerike", "sverige"])
        self.__scan_text_verify_matches(finder, "the apple is red", [])
        self.__scan_text_verify_matches(finder, "", [])
        self.__scan_text_verify_matches(finder,
                                        "apple computer banan foo sverige ben reddik fy fasan",
                                        ["apple computer", "banan", "sverige"])
        self.__scan_text_verify_matches(finder, "a a b", ["a", "a", "a b"])

    def test_scan_matches_and_ranges(self):
        dictionary = in3120.Trie()
        dictionary.add(["eple", "drue", "appelsin", "drue appelsin rosin banan papaya"], self.__tokenizer)
        finder = in3120.StringFinder(dictionary, self.__tokenizer)
        results = list(finder.scan("et eple og en drue   appelsin  rosin banan papaya frukt"))
        self.assertListEqual(results, [{'match': 'eple', 'range': (3, 7)},
                                       {'match': 'drue', 'range': (14, 18)},
                                       {'match': 'appelsin', 'range': (21, 29)},
                                       {'match': 'drue appelsin rosin banan papaya', 'range': (14, 49)}])

    def test_uses_yield(self):
        from types import GeneratorType
        trie = in3120.Trie()
        trie.add(["foo"], self.__tokenizer)
        finder = in3120.StringFinder(trie, self.__tokenizer)
        matches = finder.scan("the foo bar")
        self.assertIsInstance(matches, GeneratorType, "Are you using yield?")

    def test_mesh_terms_in_cran_corpus(self):
        mesh = in3120.InMemoryCorpus("../data/mesh.txt")
        cran = in3120.InMemoryCorpus("../data/cran.xml")
        trie = in3120.Trie()
        trie.add((d["body"] or "" for d in mesh), self.__tokenizer)
        finder = in3120.StringFinder(trie, self.__tokenizer)
        self.__scan_text_verify_matches(finder, cran[0]["body"], ["wing", "wing"])
        self.__scan_text_verify_matches(finder, cran[3]["body"], ["solutions", "skin", "friction"])
        self.__scan_text_verify_matches(finder, cran[1254]["body"], ["electrons", "ions"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
