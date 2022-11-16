"""
    A super simple string search algorithm
"""


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
    for i in range(len(T) - len(P) + 1):
        if same(T[i:], P, len(P)):
            yield i

if __name__ == "__main__":

    needle = "abc"
    haystack = "abababdwerdfgbbcabcabaaabc"

    for i in search(needle, haystack):
        assert haystack[i:i+len(needle)] == needle
        print(i, haystack[i:i+len(needle)])
