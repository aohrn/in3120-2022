#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120


class TestBrainDeadNormalizer(unittest.TestCase):

    def setUp(self):
        self.__normalizer = in3120.BrainDeadNormalizer()

    def test_canonicalize(self):
        self.assertEqual(self.__normalizer.canonicalize("Dette ER en\nprØve!"), "Dette ER en\nprØve!")

    def test_normalize(self):
        self.assertEqual(self.__normalizer.normalize("grÅFustaSJE"), "gråfustasje")


if __name__ == '__main__':
    unittest.main(verbosity=2)
