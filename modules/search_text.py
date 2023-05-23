import numpy as np
import pandas as pd
import regex as re
from Levenshtein import distance as lev

# from unidecode import unidecode

SEP_CHAR = {
    ";",
    ":",
    "-",
    "+",
    ".",
    "?",
    "!",
    ",",
    "[",
    "]",
    "(",
    ")",
    "{",
    "}",
    "<",
    ">",
    "*",
    "~",
}
reSEP = r"[;:\-+.?!,()\[\]{}<>\*~]"
IGNORE_CHAR = {"'", '"', "”", "/", "\\", "#", "$", "%", "&", "@", "^"}
reIGNORE = r"['\"”/\\#$%&@\^]"
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


def qsp(tosort, leq):
    """
        tosort :: a list of two-entry lists, where the first entry is an index, 
        and the second entry is a value to sort by.
        leq :: a function defining a less-than-or-equal relation
        
        Chooses a pivot element from the list, and assigns all elements less-
        -than-or-equal to a list by its "left" (`l`) and all the elements
        strictly greater to a list by its "right" (`r`). Returns "left" list,
        pivot element (as a list) and the "right" list.
    """    
    l, r = [], []
    pivot = tosort[-1]
    l = [el for el in tosort[:-1] if leq(el[1], pivot[1])]
    r = [el for el in tosort if not leq(el[1], pivot[1])]
    return l, [pivot], r


def qs_eng(tosort, leq):
    """
        tosort :: a list of two-entry lists, where the first entry is an index, 
        and the second entry is a value to sort by.
        leq :: a function defining a less-than-or-equal relation
        
        Uses recursion to return a list with indices sorted by values.
    """
    if len(tosort) <= 1:
        return tosort
    l, pivot, r = qsp(tosort, leq)
    l = qs_eng(l, leq)
    r = qs_eng(r, leq)
    return l + pivot + r


def qs_df(df, col, leq, cutoff=5):
    """
        df :: pandas.DataFrame object
        col :: column to sort by
        leq :: a function defining a less-than-or-equal relation for two values,
        ie, leq(a,b) -> True if a <= b etc... reason is that this allows for
        user defined relation.
        cutoff :: the number of elements that we want to return from the `top`
        of the list.
        
        Applies the quick-sort algorithm to a DataFrame by on one of it's
        columns and based on a user defined less-than-or-equal relation. The
        algorithm actually runs on an array to speed up sorting. DataFrames are
        slower to iterate through and to change rows.
    """
    ilist = df.index.values.tolist()
    dislist = df[col].values.tolist()
    tosort = [[ilist[i], dislist[i]] for i in range(len(ilist))]
    sortlist = qs_eng(tosort, leq)
    ilist = [el[0] for el in sortlist[:cutoff]]
    sdf = df.loc[ilist]
    return sdf


def qs_part(df, column, leq): # not used
    l, r = [], []
    pivot = df.tail(1)
    l = [
        df.iloc[[i]]
        for i in list(df.index.values)
        if leq(df.iloc[i][column], pivot[column].iloc[0])
    ]
    l = pd.concat(l, ignore_index=True).head(-1)
    r = [
        df.iloc[[i]]
        for i in list(df.index.values)
        if not leq(df.iloc[i][column], pivot[column].iloc[0])
    ]
    if len(r) > 0:
        r = pd.concat(r, ignore_index=True)
    else:
        r = pd.DataFrame(dtype=int).reindex(columns=df.columns)
    return l, pivot, r


def quick_sort(df, column, leq): # not used
    if len(df) <= 1:
        return df
    l, pivot, r = qs_part(df, column, leq)
    l = quick_sort(l, column, leq)
    r = quick_sort(r, column, leq)
    return pd.concat([l, pivot, r], ignore_index=True)


def abc_leq(list_1, list_2):  # == (list_1 <= list_2)
    l = min(len(list_1), len(list_2))
    for i in range(l):
        if list_1[i] == list_2[i]:
            continue
        elif list_1[i] > list_2[i]:
            return False
        else:
            return True
    # this rewards shorter lists
    return True


def abc_order(search_word, df, column="title", cutoff=5):  # not used
    df["dis"] = df.apply(
        lambda row: token_distance_list(search_word, row[column]), axis=1
    )
    if cutoff is None:
        return quick_sort(df, column, abc_leq)
    return quick_sort(df, column, abc_leq).head(cutoff)


def tokenize_1(string):  # not used
    tokens = set(string.lower().split(" "))
    tokens = [re.sub(r"[^a-zA-Z0-9]", "", token) for token in tokens]
    tokens = [token for token in tokens if token != ""]
    return tokens


def tokenize_2(streeng):  # not used
    #
    #               ROOM FOR SERIOUS IMPROVEMENT VIA regex-es!!!!
    #                        ```````
    # ... turns out regex was slower...
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


def tokenize_3(streeng):  # not used
    # string = unidecode(streeng).lower()
    string = streeng.lower()
    for char in REPLACE_CHAR:
        string = re.sub(char, REPLACE_CHAR[char], string)
    string = re.sub(reSEP, " ", string)
    string = re.sub(reIGNORE, "", string)
    tokens = set(string.split(" "))
    tokens = [token for token in tokens if token != ""]
    return tokens


def tokenize_neighbor(streeng):
    """
        Replaces a list of strings where:
        Replaces characters that usually cannot be understood as part of a word
        with a whitespace
        Replaces quirky characters with empty string as they
        are usually part of a word, just not meaningful in a search...hmm I
        might revisit this...they are not unintelligable for python after all.
        Replaces characters with diacritics with non-diacritic equivalent.
        Splits the string by whitespaces and returns as a list, and concatenates
        a list of neighboring words concatenated (no empty strings allowed)
        ie 
        "what are# yoű)dö^ing?" 
        --> 
        ["what","are","you",doing","whatare","areyou","youdoing"]
    """
    string = streeng.lower()
    for char in SEP_CHAR:
        string = string.replace(char, " ")
    for char in IGNORE_CHAR:
        string = string.replace(char, "")
    for char in REPLACE_CHAR:
        string = string.replace(char, REPLACE_CHAR[char])
    tokens = string.split(" ")
    tokens = [token for token in tokens if token != ""]
    neigh_tokens = [tokens[i] + tokens[i + 1] for i in range(len(tokens) - 1)]
    return tokens + neigh_tokens


def tokenize_neighbor_2(streeng): # not used
    # regex proven to be slower than simple .replace()
    string = unidecode(streeng).lower()
    # string = streeng.lower()
    # for char in REPLACE_CHAR:
    # string = re.sub(char, REPLACE_CHAR[char], string)
    string = re.sub(reSEP, " ", string)
    string = re.sub(reIGNORE, "", string)
    tokens = iter(string.split(" "))
    tokens = [token for token in tokens if token != ""]
    neigh_tokens = [tokens[i] + tokens[i + 1] for i in range(len(tokens) - 1)]
    return tokens + neigh_tokens


def melamed_distance_np(in_s1, in_s2, ins_cost=1, del_cost=1, sub_cost=1): # not used
    # made by chatGPT btw
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


def jaccard_similarity(in_str1, in_str2): # not used
    # made by chatGPT btw if I recall correctly
    str1, str2 = in_str1.lower(), in_str2.lower()
    # Convert the input strings to sets of n-grams (substrings)
    n = 1
    set1 = set([str1[i : i + n] for i in range(len(str1) - n + 1)])
    set2 = set([str2[i : i + n] for i in range(len(str2) - n + 1)])

    # Calculate the Jaccard similarity using set operations
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return 1 - intersection / union


def combined_similarity(in_str1, in_str2): # not used
    j = jaccard_similarity(in_str1, in_str2)
    m = melamed_distance_np(in_str1, in_str2)
    return j * m


def token_distance(search_value, text, cutoff=5): # not used
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


def token_distance_two(search_value, text, cutoff=5): # not used
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


def token_distance_three(search_value, text, cutoff=5): # not used
    """
    Calculate the melamed distance between all the possible pair of words,
    and all the possible concatenations of neighboring words. Order the
    distances and sum them with ever decreasing weight, and normalize for
    the weight.
    """
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
    rec_norm = 2 - (1 / 2 ** (n - 1))
    return np.sum(distance_list) / rec_norm


def token_distance_list(search_value, text, cutoff=5):
    """
    Calculate the levensthein distance between all the possible pairs of words,
    and all the possible concatenations of neighboring words. Order the
    distances.
    """
    search_tokens = tokenize_neighbor(search_value)
    text_tokens = tokenize_neighbor(text)
    distance_list = []
    for token1 in search_tokens:
        if token1 in text.lower():
            distance_list.append(1)  # very close match
        for token2 in text_tokens:
            distance_list.append(lev(token1, token2))
    distance_list.sort()
    return distance_list


def token_distance_list_2(search_value, text, cutoff=5): # not used
    """
    Calculate the melamed distance between all the possible pairs of words,
    and all the possible concatenations of neighboring words but only keep the
    minimums.
    """
    search_tokens = tokenize_neighbor(search_value)
    text_tokens = tokenize_neighbor(text)
    distance_list = []
    for token1 in search_tokens:
        if token1 in text.lower():
            distance_list.append(1)  # very close match
        distance_list = distance_list + [lev(token1, token2) for token2 in text_tokens]
    distance_list.sort()
    return distance_list


def token_distance_list_3(search_value, text, cutoff=5): # not used
    """
    Calculate the melamed distance between all the possible pairs of words,
    and all the possible concatenations of neighboring words but only keep the
    minimums.
    """
    search_tokens = tokenize_neighbor(search_value)
    text_tokens = tokenize_neighbor(text)
    distance_list = [
        1 for token1 in search_tokens if token1 in text.lower()
    ]  # very close match
    for token1 in search_tokens:
        distance_list = distance_list + [lev(token1, token2) for token2 in text_tokens]
    distance_list.sort()
    return distance_list
