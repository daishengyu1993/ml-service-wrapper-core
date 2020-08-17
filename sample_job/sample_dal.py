
import pandas as pd


def process(s: pd.Series, mod_by: int = 2):
    result = pd.DataFrame(s.str.len() % mod_by)

    result.columns = ["Result"]

    return result
