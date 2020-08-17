
import pandas as pd


def process(df: pd.DataFrame, mod_by: int = 2):
    result = pd.DataFrame(df["TextField"].str.len() % mod_by)

    result.columns = ["Result"]
    result.insert(0, "Id", df["Id"])


    return result
