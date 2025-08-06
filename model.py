import base64
import json
import matplotlib.pyplot as plt
import pandas as pd
import re
from utils.data_handler import load_data_from_files, scrape_wikipedia
from utils.plotting import make_scatterplot_with_regression

def handle_query(question_path, file_paths):
    with open(question_path, "r") as f:
        questions = f.read()

    if "highest grossing films" in questions:
        df = scrape_wikipedia()
    else:
        df = load_data_from_files(file_paths)

    answers = []

    # Sample Q1: count of $2B films before 2000
    match = re.search(r'How many \$2 bn movies.*?2000', questions)
    if match:
        df["Gross"] = df["Worldwide gross"].str.replace("[$,]", "", regex=True).astype(float)
        df["Year"] = pd.to_datetime(df["Release date"]).dt.year
        count = df[(df["Gross"] >= 2e9) & (df["Year"] < 2000)].shape[0]
        answers.append(count)

    # Sample Q2: earliest film over $1.5B
    match = re.search(r'earliest film.*?1\.5 bn', questions)
    if match:
        df["Gross"] = df["Worldwide gross"].str.replace("[$,]", "", regex=True).astype(float)
        df["Year"] = pd.to_datetime(df["Release date"]).dt.year
        film = df[df["Gross"] >= 1.5e9].sort_values("Year").iloc[0]["Title"]
        answers.append(film)

    # Sample Q3: correlation between Rank and Peak
    match = re.search(r'correlation.*?Rank.*?Peak', questions)
    if match:
        corr = df["Rank"].corr(df["Peak"])
        answers.append(round(corr, 6))

    # Sample Q4: scatterplot with red regression line
    match = re.search(r'scatterplot.*?Rank.*?Peak', questions)
    if match:
        plot_uri = make_scatterplot_with_regression(df["Rank"], df["Peak"])
        answers.append(plot_uri)

    return answers
