import numpy as np
import pandas as pd
import regex as re

SEP_CHAR = {";", ":", "-", "+", ".", "?", "!", ","}
IGNORE_CHAR = {
    "'",
    '"',
    "”",
    "(",
    ")",
    "<",
    ">",
    "[",
    "]",
    "{",
    "}",
    "/",
    "\\",
}
REPLACE_CHAR = {
    "á": "a",
    "é": "e",
    "í": "i",
    "ó": "o",
    "ö": "o",
    "ő": "o",
    "ú": "u",
    "ü": "u",
    "ű": "u",
}


def abc_list_first_is_smaller(list_1, list_2):  # == (list_1 <= list_2)
    l = min(len(list_1), len(list_2))
    for i in range(l):
        if list_1[i] > list_2[i]:
            return False
    # this rewards shorter lists
    return True


def abc_order(df):
    pass
    #
    #           OH MAN, THIS NEEDS A QUICKSORT OF SOME KIND!!!
    #                                `````````


def tokenize_1(string):
    tokens = set(string.lower().split(" "))
    tokens = [re.sub(r"[^a-zA-Z0-9]", "", token) for token in tokens]
    tokens = [token for token in tokens if token != ""]
    return tokens


def tokenize_2(streeng):
    #
    #               ROOM FOR SERIOUS IMPROVEMENT VIA regex-es!!!!
    #                        ```````
    string = streeng.lower()
    for char in SEP_CHAR:
        string = string.replace(char, " ")
    for char in IGNORE_CHAR:
        string = string.replace(char, "")
    for char in REPLACE_CHAR:
        string = string.replace(char, REPLACE_CHAR[char])
    tokens = set(string.split(" "))
    tokens = [token for token in tokens if token != ""]
    return tokens


def tokenize_neighbor(streeng):
    string = streeng.lower()
    for char in SEP_CHAR:
        string = string.replace(char, " ")
    for char in IGNORE_CHAR:
        string = string.replace(char, "")
    for char in REPLACE_CHAR:
        string = string.replace(char, REPLACE_CHAR[char])
    tokens = string.split(" ")
    neigh_tokens = [tokens[i] + tokens[i + 1] for i in range(len(tokens) - 1)]
    return neigh_tokens


def melamed_distance_np(in_s1, in_s2, ins_cost=1, del_cost=1, sub_cost=1):
    s1, s2 = in_s1.lower(), in_s2.lower()
    m, n = len(s1), len(s2)
    dp = np.zeros((m + 1, n + 1), dtype=int)

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                ins = dp[i][j - 1] + ins_cost
                del_ = dp[i - 1][j] + del_cost
                sub = dp[i - 1][j - 1] + sub_cost
                dp[i][j] = min(ins, del_, sub)
                if (
                    i > 1
                    and j > 1
                    and s1[i - 1] == s2[j - 2]
                    and s1[i - 2] == s2[j - 1]
                ):
                    dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + sub_cost)

    return dp[m][n]


def jaccard_similarity(in_str1, in_str2):
    str1, str2 = in_str1.lower(), in_str2.lower()
    # Convert the input strings to sets of n-grams (substrings)
    n = 1
    set1 = set([str1[i : i + n] for i in range(len(str1) - n + 1)])
    set2 = set([str2[i : i + n] for i in range(len(str2) - n + 1)])

    # Calculate the Jaccard similarity using set operations
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return 1 - intersection / union


def combined_similarity(in_str1, in_str2):
    j = jaccard_similarity(in_str1, in_str2)
    m = melamed_distance_np(in_str1, in_str2)
    return j * m


def sort_token(search_value, list_of_strings, cutoff=None, method=1):
    sorted = pd.DataFrame(columns=["string", "token"])
    if method == 1:
        for string in list_of_strings:
            token_d = token_distance(search_value, string)
            sorted = sorted.append(
                {
                    "string": string,
                    "token": token_d,
                },
                ignore_index=True,
            )
    elif method == 2:
        for string in list_of_strings:
            token_d = token_distance_two(search_value, string)
            sorted = sorted.append(
                {
                    "string": string,
                    "token": token_d,
                },
                ignore_index=True,
            )
    else:
        for string in list_of_strings:
            token_d = token_distance_three(search_value, string)
            sorted = sorted.append(
                {
                    "string": string,
                    "token": token_d,
                },
                ignore_index=True,
            )
    if cutoff is not None:
        df = sorted.sort_values(by=["token"]).head(cutoff)
        for line in df["string"]:
            print(tokenize_1(line))
            print(tokenize_2(line))
            print(tokenize_neighbor(line))
            print()
        return sorted.sort_values(by=["token"]).head(cutoff)
    return sorted.sort_values(by=["token"])


def token_distance(search_value, text, cutoff=5):
    """
    Calculate the tokenized distance of for each pair of strings and create
    a list of sorted match values.
    """
    search_tokens, text_tokens = tokenize_1(search_value), tokenize_1(text)
    distance_list = []
    for token1 in search_tokens:
        for token2 in text_tokens:
            distance_list.append(melamed_distance_np(token1, token2))
    distance_list.sort()
    distance_list = [d / 2**i for i, d in enumerate(distance_list)]
    n = len(distance_list)
    rec_norm = -2 * (0.5**n - 1)
    return np.sum(distance_list) / rec_norm


def token_distance_two(search_value, text, cutoff=5):
    """ """
    search_tokens, text_tokens = tokenize_2(search_value), tokenize_2(text)
    distance_list = []
    for token1 in search_tokens:
        for token2 in text_tokens:
            distance_list.append(melamed_distance_np(token1, token2))
    distance_list.sort()
    distance_list = [d / 2**i for i, d in enumerate(distance_list)]
    n = len(distance_list)
    rec_norm = -2 * (0.5**n - 1)
    return np.sum(distance_list) / rec_norm


def token_distance_three(search_value, text, cutoff=5):
    """ """
    search_tokens = tokenize_2(search_value) + tokenize_neighbor(search_value)
    text_tokens = tokenize_2(text) + tokenize_neighbor(text)

    distance_list = []
    very_close_match = []
    for token1 in search_tokens:
        for token2 in text_tokens:
            distance_list.append(melamed_distance_np(token1, token2))
    distance_list.sort()
    distance_list = [d / 2**i for i, d in enumerate(distance_list)]
    n = len(distance_list)
    rec_norm = -2 * (0.5**n - 1)
    print(rec_norm)
    return np.sum(distance_list) / rec_norm


def main():
    doc = "music_lib - arch.txt"
    list_of_strings = []
    with open(doc) as r:
        for line in r:
            list_of_strings.append(line.split(" -- ")[0])

    search_value = input("Search phrase>> ")
    maszlag = "bikki nee hrree"
    # print(sort_by_lev(search_value, list_of_strings))
    # print(sort_by_jac(search_value, list_of_strings))
    # print(sort_lev_jac(search_value, list_of_strings))
    # print(sort_token(search_value, list_of_strings))
    print_values = True
    print(sort_token(search_value, list_of_strings, cutoff=5, method=1))
    print(sort_token(search_value, list_of_strings, cutoff=5, method=2))
    print(sort_token(search_value, list_of_strings, cutoff=5, method=3))
    # print(token_distance(search_value, maszlag))


if __name__ == "__main__":
    main()
