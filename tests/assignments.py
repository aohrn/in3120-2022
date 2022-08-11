#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest
from typing import List


def build_test_suite(test_cases: List[str]) -> unittest.TestSuite:
    import tests
    suite = unittest.TestSuite()
    for test_case in test_cases:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(tests, test_case)))
    return suite


def assignment_a_suite() -> unittest.TestSuite:
    return build_test_suite(["TestInMemoryInvertedIndexWithoutCompression", "TestPostingsMerger"])


def assignment_b_suite() -> unittest.TestSuite:
    return build_test_suite(["TestSuffixArray", "TestTrie", "TestStringFinder"])


def assignment_c_suite() -> unittest.TestSuite:
    return build_test_suite(["TestSimpleSearchEngine"])


def assignment_d_suite() -> unittest.TestSuite:
    return build_test_suite(["TestBetterRanker", "TestShingleGenerator"])


def assignment_e_suite() -> unittest.TestSuite:
    return build_test_suite(["TestNaiveBayesClassifier"])


def assignment_x_suite() -> unittest.TestSuite:
    return build_test_suite(["TestBrainDeadNormalizer", "TestBrainDeadTokenizer", "TestInMemoryDictionary",
                             "TestInMemoryDocument", "TestInMemoryCorpus", "TestSieve", "TestVariableByteCodec",
                             "TestInMemoryPostingList", "TestCompressedInMemoryPostingList",
                             "TestInMemoryInvertedIndexWithCompression", "TestExpressionComposer",
                             "TestShallowCaseExtractor", "TestDocumentPipeline"])


def main():
    tests = {"a": assignment_a_suite,
             "b": assignment_b_suite,
             "c": assignment_c_suite,
             "d": assignment_d_suite,
             "e": assignment_e_suite,
             "x": assignment_x_suite}
    targets = sys.argv[1:] or tests.keys()
    suite = unittest.TestSuite()
    for target in targets:
        suite.addTests(tests[target.lower()]())
    if suite.countTestCases() > 0:
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)


if __name__ == "__main__":
    main()
