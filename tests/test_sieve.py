#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120


class TestSieve(unittest.TestCase):

    def test_sifting(self):
        sieve = in3120.Sieve(3)
        sieve.sift(1.0, "one")
        sieve.sift(10.0, "ten")
        sieve.sift(9.0, "nine")
        sieve.sift(2.0, "two")
        sieve.sift(5.0, "five")
        sieve.sift(8.0, "eight")
        sieve.sift(7.0, "seven")
        sieve.sift(6.0, "six")
        sieve.sift(3.0, "three")
        sieve.sift(4.0, "four")
        self.assertListEqual(list(sieve.winners()), [(10.0, "ten"), (9.0, "nine"), (8.0, "eight")])

    def test_invalid_size(self):
        for i in [-1, 0]:
            with self.assertRaises(AssertionError):
                in3120.Sieve(i)

    def test_empty_sieve(self):
        sieve = in3120.Sieve(3)
        self.assertListEqual(list(sieve.winners()), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
