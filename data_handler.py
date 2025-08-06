import pandas as pd
import os

def load_data_from_files(file_paths):
    for fname, path in file_paths.items():
        if fname.endswith(".csv"):
            return pd.read_csv(path)
        elif fname.endswith(".parquet"):
            return pd.read_parquet(path)
    return pd.DataFrame()

def scrape_wikipedia():
    import requests
    import pandas as pd
    tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_highest-grossing_films")
    return tables[0]
