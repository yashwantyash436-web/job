import pandas as pd

def load_data():
    df = pd.read_csv("data/AI_Impact_on_Jobs_2030.csv")
    return df
