#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import operator
from collections import Counter
from .dictionary import InMemoryDictionary
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .corpus import Corpus
from typing import Any, Dict, Iterable, Iterator


class NaiveBayesClassifier:
    """
    Defines a multinomial naive Bayes text classifier.
    """

    def __init__(self, training_set: Dict[str, Corpus], fields: Iterable[str],
                 normalizer: Normalizer, tokenizer: Tokenizer):
        """
        Constructor. Trains the classifier from the named fields in the documents in
        the given training set.
        """
        # Used for breaking the text up into discrete classification features.
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer

        # The vocabulary we've seen during training.
        self.__vocabulary = InMemoryDictionary()

        # Maps a category c to the prior probability Pr(c).
        self.__priors: Dict[str, float] = {}

        # Maps a category c and a term t to the conditional probability Pr(t | c).
        self.__conditionals: Dict[str, Dict[str, float]] = {}

        # So that we know how to estimate Pr(t | c) for out-of-vocabulary terms encountered
        # in the texts to classify. Basically the denominators when doing Laplace smoothing,
        # for each category c.
        self.__denominators: Dict[str, int] = {}

        # Train the classifier, i.e., estimate all probabilities.
        self.__compute_priors(training_set)
        self.__compute_vocabulary(training_set, fields)
        self.__compute_posteriors(training_set, fields)

    def __compute_priors(self, training_set):
        """
        Estimates all prior probabilities needed for the naive Bayes classifier.
        """

        # Maximum likelihood estimate.
        total_count = sum([training_set[category].size() for category in training_set])
        self.__priors = {category: training_set[category].size() / total_count for category in training_set}

    def __compute_vocabulary(self, training_set, fields):
        """
        Builds up the overall vocabulary as seen in the training set.
        """
        # We're doing simple add-one (Laplace) smoothing when estimating the probabilities, so
        # figure out the size of the overall vocabulary.
        for (_, corpus) in training_set.items():
            for document in corpus:
                for field in fields:
                    for term in self.__get_terms(document.get_field(field, "")):
                        self.__vocabulary.add_if_absent(term)

    def __compute_posteriors(self, training_set, fields):
        """
        Estimates all conditional probabilities needed for the naive Bayes classifier.
        """
        # Use smoothed estimates. Remember the denominators we used, so that we later know how
        # to handle out-of-vocabulary words.
        for (category, corpus) in training_set.items():
            terms = self.__get_terms(" ".join([d.get_field(f, "") for d in corpus for f in fields]))
            term_frequencies = Counter(terms)
            self.__denominators[category] = sum(term_frequencies.values()) + self.__vocabulary.size()
            self.__conditionals[category] = {t: (term_frequencies[t] + 1) / self.__denominators[category]
                                             for t in term_frequencies}

    def __get_terms(self, buffer):
        """
        Processes the given text buffer and returns the sequence of normalized
        terms as they appear. Both the documents in the training set and the buffers
        we classify need to be identically processed.
        """
        tokens = self.__tokenizer.strings(self.__normalizer.canonicalize(buffer))
        return (self.__normalizer.normalize(t) for t in tokens)

    def classify(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Classifies the given buffer according to the multinomial naive Bayes rule. The computed (score, category) pairs
        are emitted back to the client via the supplied callback sorted according to the scores. The reported scores
        are log-probabilities, to minimize numerical underflow issues. Logarithms are base e.

        The results yielded back to the client are dictionaries having the keys "score" (float) and
        "category" (str).
        """
        # Only consider terms that occurred in the training set.
        terms = [term for term in self.__get_terms(buffer) if term in self.__vocabulary]

        # Seed with priors.
        scores = {category: math.log(self.__priors[category]) for category in self.__priors}

        # Accumulate log-probabilities for each term. For terms not observed for the current category,
        # use a smoothed estimate.
        for category in scores:
            default = 1.0 / self.__denominators[category]
            for term in terms:
                scores[category] += math.log(self.__conditionals[category].get(term, default))

        # Emit categories back to the client in sorted order.
        for (category, score) in reversed(sorted(scores.items(), key=operator.itemgetter(1))):
            yield {"score": score, "category": category}
