#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define ALPHABET_LEN 256

/* Print occurrence with context */
void print_context(int skip, char *string, size_t stringlen,
                   char *pat, size_t patlen)
{
    printf("string[%d]: ", skip);
    printf(" ... ");
    for (int i = 10; (i > 0)
            && (skip - i > 0)
            && (string[skip - i] != '\n'); i--)
        printf("%c", string[skip - i]);
    for (int i = 0; (i < patlen + 10)
            && (skip + i < stringlen)
            && (string[skip + i] != '\n'); i++)
        printf("%c", string[skip + i]);
    printf(" ... \n");
}

/* Create table with skip values for each character (Bad character rule) */
void preprocess(int *bad_chars, char *pat, size_t patlen)
{
    for (int i = 0; i < ALPHABET_LEN; i++) {
        bad_chars[i] = patlen;
    }
    for (int i = 0; i < patlen - 1; i++) {
        bad_chars[(uint8_t) pat[i]] = patlen - 1 - i;
    }
}

/* Test string equality */
bool same(char *str1, char *str2, int l)
{
    /*
    int i = l - 1;
    while (str1[i] == str2[i]) {
        if (i == 0)
            return true;
        i -= 1;
    }

    return false;
    */

    /* `memcmp` is much more optimized */
    return (memcmp(str1, str2, l) == 0);
}

/* Boyer--Moore--Horspool algorithm */
int horspool(char *string, size_t stringlen, char *pat, size_t patlen)
{
    int bad_chars[ALPHABET_LEN];
    int skip;
    int occurences;

    occurences = 0;
    preprocess(bad_chars, pat, patlen);

    if (patlen == 0)
        return 0;

    skip = 0;
    while (stringlen - skip >= patlen) {
        if (same(&string[skip], pat, patlen)) {
            /* print_context(skip, string, stringlen, pat, patlen); */
            occurences++;
        }
        skip += bad_chars[(uint8_t) string[skip + patlen - 1]];
    }

    return occurences;
}

/* Naїve search */
int naive(char *string, size_t stringlen, char *pat, size_t patlen)
{
    int occurences;

    occurences = 0;

    if (patlen == 0)
        return 0;

    for (int i = 0; stringlen - i >= patlen; i++) {
        if (same(&string[i], pat, patlen)) {
            /* print_context(i, string, stringlen, pat, patlen); */
            occurences++;
        }
    }

    return occurences;
}


int main(int argc, char *argv[])
{
    FILE *fp;
    char *text;
    long len;
    int occurences;
    bool naive_search = false;
    char opt;

    clock_t time;
    float msec;

    /* Parse commandline options */
    while ((opt = getopt(argc, argv, "n")) != -1) {
        switch (opt) {
            case 'n':
                naive_search = true;
                break;
            case 'h':
                printf("usage: %s [-h] [-n] <pattern> <text_file>\n", argv[0]);
                exit(EXIT_SUCCESS);
        }
    }

    if (argc < 3 || argc > 5) {
        printf("usage: %s [-h] [-n] <pattern> <text_file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    /* Open file */
    fp = fopen(argv[argc - 1], "r");
    if (fp == NULL) {
        perror("Error opening file\n");
        exit(EXIT_FAILURE);
    }

    /* Find length of file */
    fseek(fp, 0, SEEK_END);
    len = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    text = malloc(len + 1);
    text[len] = '\0';

    /* Read file to memory */
    if (text)
        fread(text, 1, len, fp);
    fclose(fp);

    /* Start timer */
    time = clock();

    /* Search for pattern in text string */
    printf("Searching file ...\n");
    if (naive_search)
        occurences = naive(text, len, argv[argc-2], strlen(argv[argc-2]));
    else
        occurences = horspool(text, len, argv[argc-2], strlen(argv[argc-2]));

    /* Calculate time difference. Convert to milliseconds */
    time = clock() - time;
    msec = ((float)time / CLOCKS_PER_SEC) * 1000;

    printf("Found %d occurences in %.0fmsec\n", occurences, msec);

    free(text);
    exit(EXIT_SUCCESS);
}
