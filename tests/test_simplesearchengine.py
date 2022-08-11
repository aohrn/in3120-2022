#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120


class TestSimpleSearchEngine(unittest.TestCase):

    def setUp(self):
        self.__normalizer = in3120.BrainDeadNormalizer()
        self.__tokenizer = in3120.BrainDeadTokenizer()

    def __process_two_term_query_verify_matches(self, query, engine, options, expected):
        ranker = in3120.BrainDeadRanker()
        hits, winners = expected
        matches = list(engine.evaluate(query, options, ranker))
        matches = [(m["score"], m["document"].document_id) for m in matches]
        self.assertEqual(len(matches), hits)
        for (score, winner) in matches[:len(winners)]:
            self.assertEqual(score, 2.0)
            self.assertIn(winner, winners)
        for (score, contender) in matches[len(winners):]:
            self.assertEqual(score, 1.0)

    def test_mesh_corpus(self):
        corpus = in3120.InMemoryCorpus("../data/mesh.txt")
        index = in3120.InMemoryInvertedIndex(corpus, ["body"], self.__normalizer, self.__tokenizer)
        engine = in3120.SimpleSearchEngine(corpus, index)
        query = "polluTION Water"
        self.__process_two_term_query_verify_matches(query, engine,
                                                     {"match_threshold": 0.1, "hit_count": 10},
                                                     (10, [25274, 25275, 25276]))
        self.__process_two_term_query_verify_matches(query, engine,
                                                     {"match_threshold": 1.0, "hit_count": 10},
                                                     (3, [25274, 25275, 25276]))

    def _process_query_verify_matches(self, query, engine, options, expected):
        from itertools import takewhile
        ranker = in3120.BrainDeadRanker()
        hits, score, winners = expected
        matches = list(engine.evaluate(query, options, ranker))
        matches = [(m["score"], m["document"].document_id) for m in matches]
        self.assertEqual(len(matches), hits)
        if matches:
            for i in range(1, hits):
                self.assertGreaterEqual(matches[i - 1][0], matches[i][0])
            if score:
                self.assertEqual(matches[0][0], score)
            if winners:
                top = takewhile(lambda m: m[0] == matches[0][0], matches)
                self.assertListEqual(winners, list(sorted([m[1] for m in top])))

    def test_synthetic_corpus(self):
        from itertools import product, combinations_with_replacement
        corpus = in3120.InMemoryCorpus()
        words = ("".join(term) for term in product("bcd", "aei", "jkl"))
        texts = (" ".join(word) for word in combinations_with_replacement(words, 3))
        for text in texts:
            corpus.add_document(in3120.InMemoryDocument(corpus.size(), {"a": text}))
        index = in3120.InMemoryInvertedIndex(corpus, ["a"], self.__normalizer, self.__tokenizer)
        engine = in3120.SimpleSearchEngine(corpus, index)
        epsilon = 0.0001
        self._process_query_verify_matches("baj BAJ    baj", engine,
                                           {"match_threshold": 1.0, "hit_count": 27},
                                           (27, 9.0, [0]))
        self._process_query_verify_matches("baj caj", engine,
                                           {"match_threshold": 1.0, "hit_count": 100},
                                           (27, None, None))
        self._process_query_verify_matches("baj caj daj", engine,
                                           {"match_threshold": 2/3 + epsilon, "hit_count": 100},
                                           (79, None, None))
        self._process_query_verify_matches("baj caj", engine,
                                           {"match_threshold": 2/3 + epsilon, "hit_count": 100},
                                           (100, 3.0, [0, 9, 207, 2514]))
        self._process_query_verify_matches("baj cek dil", engine,
                                           {"match_threshold": 1.0, "hit_count": 10},
                                           (1, 3.0, [286]))
        self._process_query_verify_matches("baj cek dil", engine,
                                           {"match_threshold": 1.0, "hit_count": 10},
                                           (1, None, None))
        self._process_query_verify_matches("baj cek dil", engine,
                                           {"match_threshold": 2/3 + epsilon, "hit_count": 80},
                                           (79, 3.0, [13, 26, 273, 286, 377, 3107, 3198]))
        self._process_query_verify_matches("baj xxx yyy", engine,
                                           {"match_threshold": 2/3 + epsilon, "hit_count": 100},
                                           (0, None, None))
        self._process_query_verify_matches("baj xxx yyy", engine,
                                           {"match_threshold": 2/3 - epsilon, "hit_count": 100},
                                           (100, None, None))

    def test_document_at_a_time_traversal_mesh_corpus(self):
        from typing import Iterator, List, Tuple, Set

        class AccessLoggedCorpus(in3120.Corpus):
            def __init__(self, wrapped: in3120.Corpus):
                self.__wrapped = wrapped
                self.__accesses = set()

            def __iter__(self):
                return iter(self.__wrapped)

            def size(self) -> int:
                return self.__wrapped.size()

            def get_document(self, document_id: int) -> in3120.Document:
                self.__accesses.add(document_id)
                return self.__wrapped.get_document(document_id)

            def get_history(self) -> Set[int]:
                return self.__accesses

        class AccessLoggedIterator(Iterator[in3120.Posting]):
            def __init__(self, term: str, accesses: List[Tuple[str, int]], wrapped: Iterator[in3120.Posting]):
                self.__term = term
                self.__accesses = accesses
                self.__wrapped = wrapped

            def __next__(self):
                posting = next(self.__wrapped)
                self.__accesses.append((self.__term, posting.document_id))
                return posting

        class AccessLoggedInvertedIndex(in3120.InvertedIndex):
            def __init__(self, wrapped: in3120.InvertedIndex):
                self.__wrapped = wrapped
                self.__accesses = []

            def get_terms(self, buffer: str) -> Iterator[str]:
                return self.__wrapped.get_terms(buffer)

            def get_postings_iterator(self, term: str) -> Iterator[in3120.Posting]:
                return AccessLoggedIterator(term, self.__accesses, self.__wrapped.get_postings_iterator(term))

            def get_document_frequency(self, term: str) -> int:
                return self.__wrapped.get_document_frequency(term)

            def get_history(self) -> List[Tuple[str, int]]:
                return self.__accesses

        corpus1 = in3120.InMemoryCorpus("../data/mesh.txt")
        corpus2 = AccessLoggedCorpus(corpus1)
        index = AccessLoggedInvertedIndex(in3120.InMemoryInvertedIndex(corpus1, ["body"],
                                                                       self.__normalizer, self.__tokenizer))
        engine = in3120.SimpleSearchEngine(corpus2, index)
        ranker = in3120.BrainDeadRanker()
        query = "Water  polluTION"
        options = {"match_threshold": 0.5, "hit_count": 1, "debug": False}
        matches = list(engine.evaluate(query, options, ranker))
        self.assertIsNotNone(matches)
        history = corpus2.get_history()
        self.assertListEqual(list(history), [25274])  # Only the document in the result set should be accessed.
        ordering1 = [('water', 3078),  # Document-at-a-time ordering if evaluated as "water pollution".
                     ('pollution', 788), ('pollution', 789), ('pollution', 790), ('pollution', 8079),
                     ('water', 8635),
                     ('pollution', 23837),
                     ('water', 9379), ('water', 23234), ('water', 25265),
                     ('pollution', 25274),
                     ('water', 25266), ('water', 25267), ('water', 25268), ('water', 25269), ('water', 25270),
                     ('water', 25271), ('water', 25272), ('water', 25273), ('water', 25274), ('water', 25275),
                     ('pollution', 25275),
                     ('water', 25276),
                     ('pollution', 25276),
                     ('water', 25277), ('water', 25278), ('water', 25279), ('water', 25280), ('water', 25281)]
        ordering2 = [('pollution', 788),  # Document-at-a-time ordering if evaluated as "pollution water".
                     ('water', 3078),
                     ('pollution', 789), ('pollution', 790), ('pollution', 8079),
                     ('water', 8635),
                     ('pollution', 23837),
                     ('water', 9379), ('water', 23234), ('water', 25265),
                     ('pollution', 25274),
                     ('water', 25266), ('water', 25267), ('water', 25268), ('water', 25269), ('water', 25270),
                     ('water', 25271), ('water', 25272), ('water', 25273), ('water', 25274),
                     ('pollution', 25275),
                     ('water', 25275),
                     ('pollution', 25276),
                     ('water', 25276), ('water', 25277), ('water', 25278), ('water', 25279), ('water', 25280),
                     ('water', 25281)]
        history = index.get_history()
        self.assertTrue(history == ordering1 or history == ordering2)  # Strict.

    def test_uses_yield(self):
        import types
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"a": "foo bar"}))
        index = in3120.InMemoryInvertedIndex(corpus, ["a"], self.__normalizer, self.__tokenizer)
        engine = in3120.SimpleSearchEngine(corpus, index)
        ranker = in3120.BrainDeadRanker()
        matches = engine.evaluate("foo", {}, ranker)
        self.assertIsInstance(matches, types.GeneratorType, "Are you using yield?")


if __name__ == '__main__':
    unittest.main(verbosity=2)
