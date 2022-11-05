#!/usr/bin/python
# -*- coding: utf-8 -*-

from .ranker import Ranker
from .corpus import Corpus
from .posting import Posting
from .invertedindex import InvertedIndex
import math


class BetterRanker(Ranker):
    """
    A ranker that does traditional TF-IDF ranking, possibly combining it with
    a static document score (if present).

    The static document score is assumed accessible in a document field named
    "static_quality_score". If the field is missing or doesn't have a value, a
    default value of 0.0 is assumed for the static document score.

    See Section 7.1.4 in https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self._score = 0.0
        self._document_id = None
        self._corpus = corpus
        self._inverted_index = inverted_index
        self._dynamic_score_weight = 1.0  # TODO: Make this configurable.
        self._static_score_weight = 1.0  # TODO: Make this configurable.
        self._static_score_field_name = "static_quality_score"  # TODO: Make this configurable.

    def reset(self, document_id: int) -> None:
        self._score = 0.0
        self._document_id = document_id

    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        assert term is not None
        assert multiplicity > 0
        assert posting is not None
        assert posting.term_frequency > 0
        assert posting.document_id == self._document_id
        tf_score = 1.0 + math.log10(posting.term_frequency)
        idf_score = math.log10(self._corpus.size() / float(self._inverted_index.get_document_frequency(term)))
        self._score += (1.0 + math.log10(multiplicity)) * tf_score * idf_score

    def evaluate(self) -> float:
        document = self._corpus[self._document_id]
        static_quality_score = float(document[self._static_score_field_name] or 0.0)
        return (self._dynamic_score_weight * self._score) + (self._static_score_weight * static_quality_score)
