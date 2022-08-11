#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120


class TestTrie(unittest.TestCase):

    def test_access_nodes(self):
        tokenizer = in3120.BrainDeadTokenizer()
        root = in3120.Trie()
        root.add(["abba", "ørret", "abb", "abbab", "abbor"], tokenizer)
        self.assertFalse(root.is_final())
        self.assertIsNone(root.consume("snegle"))
        node = root.consume("ab")
        self.assertFalse(node.is_final())
        node = node.consume("b")
        self.assertTrue(node.is_final())
        self.assertEqual(node, root.consume("abb"))


if __name__ == '__main__':
    unittest.main(verbosity=2)
