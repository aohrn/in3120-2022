#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from typing import Callable, Any
from context import in3120


def data_path(filename: str):
    return "../data/" + filename


def simple_repl(prompt: str, evaluator: Callable[[str], Any]):
    from timeit import default_timer as timer
    import pprint
    printer = pprint.PrettyPrinter()
    escape = "!"
    print(f"Enter '{escape}' to exit.")
    while True:
        print(f"{prompt}>", end="")
        query = input()
        if query == escape:
            break
        start = timer()
        matches = evaluator(query)
        end = timer()
        printer.pprint(matches)
        print(f"Evaluation took {end - start} seconds.")


def repl_a():
    print("Building inverted index from Cranfield corpus...")
    normalizer = in3120.BrainDeadNormalizer()
    tokenizer = in3120.BrainDeadTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("cran.xml"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    print("Enter one or more index terms and inspect their posting lists.")
    simple_repl("terms", lambda ts: {t: list(index.get_postings_iterator(t)) for t in index.get_terms(ts)})


def repl_b_1():
    print("Building suffix array from Cranfield corpus...")
    normalizer = in3120.BrainDeadNormalizer()
    tokenizer = in3120.BrainDeadTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("cran.xml"))
    engine = in3120.SuffixArray(corpus, ["body"], normalizer, tokenizer)
    options = {"debug": False, "hit_count": 5}
    print("Enter a prefix phrase query and find matching documents.")
    print(f"Lookup options are {options}.")
    print("Returned scores are occurrence counts.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options)))


def repl_b_2():
    print("Building trie from MeSH corpus...")
    normalizer = in3120.BrainDeadNormalizer()
    tokenizer = in3120.BrainDeadTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("mesh.txt"))
    dictionary = in3120.Trie()
    dictionary.add((normalizer.normalize(normalizer.canonicalize(d["body"])) for d in corpus), tokenizer)
    engine = in3120.StringFinder(dictionary, tokenizer)
    print("Enter some text and locate words and phrases that are MeSH terms.")
    simple_repl("text", lambda t: list(engine.scan(normalizer.normalize(normalizer.canonicalize(t)))))


def repl_c():
    print("Indexing English news corpus...")
    normalizer = in3120.BrainDeadNormalizer()
    tokenizer = in3120.BrainDeadTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BrainDeadRanker()
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_1():
    print("Indexing MeSH corpus...")
    normalizer = in3120.BrainDeadNormalizer()
    tokenizer = in3120.ShingleGenerator(3)
    corpus = in3120.InMemoryCorpus(data_path("mesh.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BrainDeadRanker()
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_2():
    print("Indexing English news corpus...")
    normalizer = in3120.BrainDeadNormalizer()
    tokenizer = in3120.BrainDeadTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_e():
    print("Initializing naive Bayes classifier from news corpora...")
    normalizer = in3120.BrainDeadNormalizer()
    tokenizer = in3120.BrainDeadTokenizer()
    languages = ["en", "no", "da", "de"]
    training_set = {language: in3120.InMemoryCorpus(data_path(f"{language}.txt")) for language in languages}
    classifier = in3120.NaiveBayesClassifier(training_set, ["body"], normalizer, tokenizer)
    print(f"Enter some text and classify it into {languages}.")
    print(f"Returned scores are log-probabilities.")
    simple_repl("text", lambda t: list(classifier.classify(t)))


def repl_x_1():
    extractor = in3120.ShallowCaseExtractor()
    print(f"Enter some text and see what gets extracted based on simple case heuristics.")
    simple_repl("text", lambda t: list(extractor.extract(t)))


def main():
    repls = {"a": repl_a,
             "b-1": repl_b_1,
             "b-2": repl_b_2,
             "c": repl_c,
             "d-1": repl_d_1,
             "d-2": repl_d_2,
             "e": repl_e,
             "x-1": repl_x_1}
    targets = sys.argv[1:]
    if not targets:
        print(f"{sys.argv[0]} [{'|'.join(key for key in repls.keys())}]")
    else:
        for target in targets:
            if target in repls:
                repls[target.lower()]()


if __name__ == "__main__":
    main()
