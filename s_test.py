import pandas as pd

from modules import search_text as st

df = pd.DataFrame(
    {"a": [2, 3, 6, 8, 2, 4, 1, 3], "b": [11, 44, 66, 33, 22, 33, 44, 99]}
)


def num_leq(a, b):
    return a <= b


sdf = st.quick_sort(df, "a", num_leq)
print(sdf)
