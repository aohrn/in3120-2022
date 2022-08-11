#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from typing import Optional
from context import in3120


class TestInMemoryCorpus(unittest.TestCase):

    def test_access_documents(self):
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"body": "this is a Test"}))
        corpus.add_document(in3120.InMemoryDocument(1, {"title": "prØve", "body": "en to tre"}))
        self.assertEqual(corpus.size(), 2)
        self.assertListEqual([d.document_id for d in corpus], [0, 1])
        self.assertListEqual([corpus[i].document_id for i in range(0, corpus.size())], [0, 1])
        self.assertListEqual([corpus.get_document(i).document_id for i in range(0, corpus.size())], [0, 1])

    def test_load_from_file(self):
        corpus = in3120.InMemoryCorpus("../data/mesh.txt")
        self.assertEqual(corpus.size(), 25588)
        corpus = in3120.InMemoryCorpus("../data/cran.xml")
        self.assertEqual(corpus.size(), 1400)
        corpus = in3120.InMemoryCorpus("../data/docs.json")
        self.assertEqual(corpus.size(), 13)
        corpus = in3120.InMemoryCorpus("../data/imdb.csv")
        self.assertEqual(corpus.size(), 1000)

    def _drop_document_if_it_contains_the_in_body(self, document: in3120.Document) -> Optional[in3120.Document]:
        return None if "the" in document.get_field("body", "") else document

    def test_load_from_file_but_drop_documents_that_contain_the_in_body(self):
        pipeline = in3120.DocumentPipeline([self._drop_document_if_it_contains_the_in_body])
        corpus = in3120.InMemoryCorpus("../data/mesh.txt", pipeline)
        self.assertEqual(corpus.size(), 25017)
        corpus = in3120.InMemoryCorpus("../data/cran.xml", pipeline)
        self.assertEqual(corpus.size(), 8)
        corpus = in3120.InMemoryCorpus("../data/docs.json", pipeline)
        self.assertEqual(corpus.size(), 0)
        corpus = in3120.InMemoryCorpus("../data/imdb.csv", pipeline)
        self.assertEqual(corpus.size(), 1000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
