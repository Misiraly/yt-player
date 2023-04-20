import numpy as np
import pandas as pd
import regex as re


def tokenize_1(string):
    tokens = set(string.lower().split(" "))
    tokens = [re.sub(r"[^a-zA-Z0-9]", "", token) for token in tokens]
    tokens = [token for token in tokens if token != ""]
    return tokens


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
    return jaccard_similarity(in_str1, in_str2) * melamed_distance_np(in_str1, in_str2)


def sort_by_lev(search_value, list_of_strings):
    sorted = pd.DataFrame(columns=["string", "distance"])
    for string in list_of_strings:
        sorted = sorted.append(
            {"string": string, "distance": melamed_distance_np(search_value, string)},
            ignore_index=True,
        )

    return sorted.sort_values(by=["distance"])


def sort_by_jac(search_value, list_of_strings):
    sorted = pd.DataFrame(columns=["string", "distance"])
    for string in list_of_strings:
        sorted = sorted.append(
            {"string": string, "distance": jaccard_similarity(search_value, string)},
            ignore_index=True,
        )

    return sorted.sort_values(by=["distance"])


def sort_lev_jac(search_value, list_of_strings):
    sorted = pd.DataFrame(columns=["string", "lev", "jac", "comb"])
    for string in list_of_strings:
        mel = melamed_distance_np(search_value, string)
        jac = jaccard_similarity(search_value, string)
        comb = mel * jac
        sorted = sorted.append(
            {"string": string, "lev": mel, "jac": jac, "comb": comb}, ignore_index=True
        )

    return sorted.sort_values(by=["comb"])


def sort_token(search_value, list_of_strings, cutoff=None, method=1):
    sorted = pd.DataFrame(columns=["string", "lev", "jac", "comb", "token"])
    if method == 1:    
        for string in list_of_strings:
            mel = melamed_distance_np(search_value, string)
            jac = jaccard_similarity(search_value, string)
            comb = mel * jac
            token_d = token_distance(search_value, string)
            sorted = sorted.append(
                {"string": string, "lev": mel, "jac": jac, "comb": comb, "token": token_d},
                ignore_index=True,
            )
    else:
        for string in list_of_strings:
            token_d = token_distance_two(search_value, string)
            sorted = sorted.append(
                {"string": string, "token": token_d},ignore_index=True,
            )
                
    if cutoff is not None:
        return sorted.sort_values(by=["token"]).head(cutoff)
    return sorted.sort_values(by=["token"])
    
    


def token_distance(search_value, text, cutoff=5):
    """ """
    search_tokens, text_tokens = tokenize_1(search_value), tokenize_1(text)
    s_length, t_length = len(search_tokens), len(text_tokens)
    distance_list = []
    # 
    for token1 in search_tokens:
        for token2 in text_tokens:
            distance_list.append(melamed_distance_np(token1, token2))
    distance_list.sort()
    distance_list = [d/2**i for i,d in enumerate(distance_list)]
    n = len(distance_list)
    rec_norm = -2*(0.5**(n+1) - 1 )
    # distance_list = np.prod(distance_list[:10])
    # print(distance_list)
    return np.sum(distance_list)/rec_norm
    # return np.prod(distance_list[:10])
        
        
def token_distance_two(search_value, text, cutoff=5):
    """ """
    search_tokens, text_tokens = tokenize_1(search_value), tokenize_1(text)
    s_length, t_length = len(search_tokens), len(text_tokens)
    norm = len(search_tokens)/len(text_tokens)
    distance_list = []
    # print(text_tokens, search_tokens)
    for token1 in search_tokens:
        for token2 in text_tokens:
            distance_list.append(melamed_distance_np(token1, token2))
    distance_list.sort()
    # distance_list = [d/2**(i+1) for i, d in enumerate(distance_list)]
    # print(distance_list)
    return norm*np.sum(distance_list)


def main():
    doc = (
        r"C:\Users\mihaly.kotiers\Desktop\trhow\yt-player\modules\music_lib - arch.txt"
    )
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
    # print(token_distance(search_value, maszlag))


if __name__ == "__main__":
    main()
