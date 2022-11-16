"""
    Quick and dirty implementation of the Boyer-Moore-Horspool algorithm
"""
import string

# Allowed characters. For simplicity, set to lowercase letters in the english alphabet
alphabet = string.printable


def preprocess(P):
    """
        Generates a bad character table for pattern P.
    """
    T = {p:len(P) for p in alphabet}

    for i in range(len(P) - 1):
        T[P[i]] = len(P) - 1 - i

    return T

def same(str1, str2, l):
    """
        Checks if the first l characters of str1 and str2 are the same
    """

    i = l-1
    while str1[i] == str2[i]:
        if i == 0:
            return True

        i -= 1

    return False

def search(P, T):
    """
        Searches for each index at which pattern P appears in text T
    """

    bad_string = preprocess(P)

    skip = 0

    while len(T) - skip >= len(P):
        if same(T[skip:], P, len(P)):
            yield skip

        skip += bad_string[T[skip + len(P) - 1]]


if __name__ == "__main__":

    needle = "abc"
    haystack = "abababdwerdfgbbcabcabaaabc"

    for i in search(needle, haystack):
        assert haystack[i:i+len(needle)] == needle
        print(i, haystack[i:i+len(needle)])
