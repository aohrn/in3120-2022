#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120


class TestInMemoryInvertedIndexWithoutCompression(unittest.TestCase):

    def setUp(self):
        self._normalizer = in3120.BrainDeadNormalizer()
        self._tokenizer = in3120.BrainDeadTokenizer()
        self._compressed = False  # Compression disabled.

    def test_access_postings(self):
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"body": "this is a Test"}))
        corpus.add_document(in3120.InMemoryDocument(1, {"body": "test TEST prØve"}))
        index = in3120.InMemoryInvertedIndex(corpus, ["body"], self._normalizer, self._tokenizer, self._compressed)
        self.assertListEqual(list(index.get_terms("PRøvE wtf tesT")), ["prøve", "wtf", "test"])
        self.assertListEqual([(p.document_id, p.term_frequency) for p in index["prøve"]], [(1, 1)])
        self.assertListEqual([(p.document_id, p.term_frequency) for p in index.get_postings_iterator("wtf")], [])
        self.assertListEqual([(p.document_id, p.term_frequency) for p in index["test"]], [(0, 1), (1, 2)])
        self.assertEqual(index.get_document_frequency("wtf"), 0)
        self.assertEqual(index.get_document_frequency("prøve"), 1)
        self.assertEqual(index.get_document_frequency("test"), 2)

    def test_mesh_corpus(self):
        corpus = in3120.InMemoryCorpus("../data/mesh.txt")
        index = in3120.InMemoryInvertedIndex(corpus, ["body"], self._normalizer, self._tokenizer, self._compressed)
        self.assertEqual(len(list(index["hydrogen"])), 8)
        self.assertEqual(len(list(index["hydrocephalus"])), 2)

    def test_multiple_fields(self):
        document = in3120.InMemoryDocument(0, {
            'felt1': 'Dette er en test. Test, sa jeg. TEST!',
            'felt2': 'test er det',
            'felt3': 'test TEsT',
        })
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(document)
        index = in3120.InMemoryInvertedIndex(corpus, ['felt1', 'felt3'], self._normalizer, self._tokenizer, self._compressed)
        posting = next(index.get_postings_iterator('test'))
        self.assertEqual(posting.document_id, 0)
        self.assertEqual(posting.term_frequency, 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
