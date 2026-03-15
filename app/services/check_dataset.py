import pandas as pd

df = pd.read_csv("processed_cuad_clean_3.csv")

print("Unique labels:", df["label"].nunique())
print("\nLabel distribution:\n")
print(df["label"].value_counts())
