# Assignment D

**Deadline:** 2022-10-28

The purpose of this assignment is twofold:

- Implement a better ranker than the `BrainDeadRanker` class. For example, inverse document frequency (i.e., considering how frequent the query terms are across the corpus) and static rank (i.e., a query-independent quality score per document) are two factors that you should include.
- Realize a simple search engine that is capable of approximate matching, e.g., where the query _organik kemmistry_ matches documents containing the terms _organic chemistry_. We will do this by using a tokenizer that produces _k_-grams (i.e., overlapping "shingles" of width _k_) and combine this with _n_-of-_m_ matching. For example, for _k_ = 3, the string _banana_ would be tokenized into the shingles {_ban_, _ana_, _nan_, _ana_}.

Your solution should only contain edits to the files `shinglegenerator.py` and `betterranker.py`. Changes to other files will be ignored.

Implementation notes:

- The `BetterRanker` class implements a better ranker than the `BrainDeadRanker` class.
- You are not required to compute a static rank score _g(d)_ for each document _d_, but can for the sake of simplicity assume that this value is stored in a suitably named document field. If the named field is missing or doesn't have a value, a default static rank score of 0.0 can be assumed.
- The `ShingleGenerator` class implements a tokenizer that produces shingles.

Your task is to:

- Familiarize yourself with the precode.
- Implement the missing code in the `BetterRanker` class.
- Implement the missing code in the `ShingleGenerator` class.
- Ensure that the code is correct and passes all tests.

Some optional bonus challenges for the interested student:

- Extend your `ShingleGenerator` implementation to make special provisions for the beginning and/or ending of strings, so that these are given more weight than other parts of the words. For example, _banana_ could be processed as _^banana$_ where the special marker symbols _^_ and _$_ are added as padding. Do you think this makes a difference?
- When working with shingles, the Jaccard distance between the set of shingles in the query and the set of shingles in the document is sometimes used as a relevancy measure. Write a ranker that implements this.
- Extend your ranker to additionally post-process all matches so that edit distance influences the ranking.
- Extend the `BrainDeadNormalizer` class to do naïve stemming (e.g., for terms longer than _n_ characters we only keep the first _n_ characters) or other types of linguistically motivated transformations. Do you think this makes a difference when combined with standard tokenization as performed by the `BrainDeadTokenizer` class?

Example output:

```
>cd tests
>python3 assignments.py d
test_document_id_mismatch (tests.TestBetterRanker) ... ok
test_inverse_document_frequency (tests.TestBetterRanker) ... ok
test_static_quality_score (tests.TestBetterRanker) ... ok
test_term_frequency (tests.TestBetterRanker) ... ok
test_ranges (tests.TestShingleGenerator) ... ok
test_shingled_mesh_corpus (tests.TestShingleGenerator) ... ok
test_strings (tests.TestShingleGenerator) ... ok
test_tokens (tests.TestShingleGenerator) ... ok
test_uses_yield (tests.TestShingleGenerator) ... ok

----------------------------------------------------------------------
Ran 9 tests in 2.679s

OK

>python3 repl.py d-1
Indexing MeSH corpus...
Enter a query and find matching documents.
Lookup options are {'debug': False, 'hit_count': 5, 'match_threshold': 0.5}.
Tokenizer is ShingleGenerator.
Ranker is BrainDeadRanker.
Enter '!' to exit.
query>orgaNik kemmistry
[{'document': {'document_id': 16981, 'fields': {'body': 'organic chemistry processes', 'meta': '27'}},
  'score': 8.0},
 {'document': {'document_id': 16980, 'fields': {'body': 'organic chemistry phenomena', 'meta': '27'}},
  'score': 8.0},
 {'document': {'document_id': 4411, 'fields': {'body': 'chemistry, organic', 'meta': '18'}},
  'score': 8.0},
 {'document': {'document_id': 4410, 'fields': {'body': 'chemistry, inorganic', 'meta': '20'}},
  'score': 8.0},
 {'document': {'document_id': 4408, 'fields': {'body': 'chemistry, bioinorganic', 'meta': '23'}},
  'score': 8.0}]
Evaluation took 0.013234000000000634 seconds.
query>!

>python3 repl.py d-2
Indexing English news corpus...
Enter a query and find matching documents.
Lookup options are {'debug': False, 'hit_count': 5, 'match_threshold': 0.5}.
Tokenizer is BrainDeadTokenizer.
Ranker is BetterRanker.
Enter '!' to exit.
query>water in the tank
[{'document': {'document_id': 7398, 'fields': {'body': 'The elevated salt levels in the water threatened some of the wildlife in the area that depend on a supply of fresh water.'}},
  'score': 1.3941246235276306},
 {'document': {'document_id': 9699, 'fields': {'body': 'While there are not many people in the water during the winter months, there are plenty playing by the shore with their jeans rolled up just enough so t
hat they can feel the cool water lap up against their feet.'}},
  'score': 1.313894761437516},
 {'document': {'document_id': 157, 'fields': {'body': "A Chinese People's Liberation Army cadet sits in a Main Battle Tank during a demonstration at the PLA's Armoured Forces Engineering Academy Base, July 22
, 2014."}},
  'score': 1.2521843989957548},
 {'document': {'document_id': 2818, 'fields': {'body': 'He noted that 50 percent of his 71 Shark Tank investments have been in female-led companies.'}},
  'score': 1.1974759616298138},
 {'document': {'document_id': 4515, 'fields': {'body': 'Kate Kralman, who shot the video of the MAX going through the water, was helping a friend load equipment nearby when she saw one light rail train go thr
ough the water.'}},
  'score': 1.176740906290895}]
Evaluation took 0.06133769999999927 seconds.
query>!
```
