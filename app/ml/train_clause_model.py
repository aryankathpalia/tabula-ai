import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import lightgbm as lgb
from sentence_transformers import SentenceTransformer

  
# CONFIG
  

DATA_PATH = "processed_cuad_clean.csv"
MODEL_PATH = "clause_model.pkl"
ENCODER_PATH = "label_encoder.pkl"
RANDOM_STATE = 42

  
# 1️ Load Dataset
  

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

print("Dataset size:", len(df))
print("Class distribution:")
print(df["label"].value_counts())
print()

  
# 2️ Encode Labels
  

print("Encoding labels...")
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df["label"])

  
# 3️ Generate Embeddings
  

print("Loading embedding model (mpnet)...")
embedder = SentenceTransformer("all-mpnet-base-v2")

print("Generating embeddings...")
X = embedder.encode(
    df["clause_text"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

  
# 4️ Stratified Split
  

print("Train/Test split...")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=RANDOM_STATE,
    stratify=y
)

  
# 5️ Train LightGBM
  

print("Training LightGBM...")

model = lgb.LGBMClassifier(
    objective="multiclass",
    num_class=len(label_encoder.classes_),
    class_weight="balanced",
    n_estimators=500,
    learning_rate=0.05,
    num_leaves=31,
    max_depth=-1,
    random_state=RANDOM_STATE,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train,
    eval_set=[(X_test, y_test)],
    eval_metric="multi_logloss",
    callbacks=[
        lgb.early_stopping(30),
        lgb.log_evaluation(50)
    ]
)

  
# 6️ Evaluate
  

print("\nEvaluating...\n")
y_pred = model.predict(X_test)

print(classification_report(
    y_test,
    y_pred,
    target_names=label_encoder.classes_
))

  
# 7️ Save Model
  

print("Saving model...")
joblib.dump(model, MODEL_PATH)
joblib.dump(label_encoder, ENCODER_PATH)

print("Training complete.")
