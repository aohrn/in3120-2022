import re
import time

import horspool
import simple_search as simple







pattern = re.compile(r"([a-zA-Z]+)")

def ranges(buffer):
    return ((m.start(), m.end()) for m in pattern.finditer(buffer))

def tokens(buffer):
    return ((buffer[r[0] : r[1]], r) for r in ranges(buffer))

def normalize(token):
    return token.lower()



if __name__ == "__main__":

    with open("shakespeare.txt") as infile:
        haystack = " ".join((normalize(token[0]) for token in tokens(infile.read())))


    #print(haystack)

    needle1 = "thy"

    needle2 = " ".join((normalize(token[0]) for token in tokens("""Unthrifty loveliness why dost thou spend,
    Upon thyself thy beauty’s legacy?
    Nature’s bequest gives nothing but doth lend,
    And being frank she lends to those are free:
    Then beauteous niggard why dost thou abuse,
    The bounteous largess given thee to give?
    Profitless usurer why dost thou use
    So great a sum of sums yet canst not live?
    For having traffic with thyself alone,
    Thou of thyself thy sweet self dost deceive,
    Then how when nature calls thee to be gone,
    What acceptable audit canst thou leave?
      Thy unused beauty must be tombed with thee,
      Which used lives th’ executor to be.""")))

    needle3 = "this sequence of letters has never appeared in any text written by shakespeare"


    results = {}

    needles = [needle1, needle2, needle3]

    for needle in needles:
        results[needle] = {}
        start = time.time()

        for i in horspool.search(needle, haystack):
            pass

        end = time.time()

        print(needle, "horspool", end-start)

        results[needle]['horspool'] = end-start

        start = time.time()

        for i in simple.search(needle, haystack):
            pass

        end = time.time()

        print(needle, "simple", end-start)

        results[needle]['simple'] = end-start


    print(results)



"""
{'thy': {'horspool': 324.75864720344543, 'simple': 1042.581699371338}, 'unthrifty loveliness why dost thou spend upon thyself thy beauty s legacy nature s bequest gives nothing but doth lend and being frank she lends to those are free then beauteous niggard why dost thou abuse the bounteous largess given thee to give profitless usurer why dost thou use so great a sum of sums yet canst not live for having traffic with thyself alone thou of thyself thy sweet self dost deceive then how when nature calls thee to be gone what acceptable audit canst thou leave thy unused beauty must be tombed with thee which used lives th executor to be': {'horspool': 34.72853708267212, 'simple': 942.0126240253448}, 'this sequence of letters has never appeared in any text written by shakespeare': {'horspool': 41.93439793586731, 'simple': 969.1292543411255}}
"""



"""
{'thy':
    {
        'horspool': 324.75864720344543,
        'simple': 1042.581699371338
    },
'unthrifty loveliness ...':
    {
        'horspool': 34.72853708267212,
        'simple': 942.0126240253448
    },
'this sequence of letters has never appeared in any text written by shakespeare':
    {
        'horspool': 41.93439793586731,
        'simple': 969.1292543411255
    }
}
"""
