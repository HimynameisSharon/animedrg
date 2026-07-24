import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import pickle
import re
import json

# ── 1. Load data ──────────────────────────────────────────────────────────────
df_raw = pd.read_excel("Desktop/data/MACHINE_DATA_EXCELSHEET_4_090725.xlsx")

# Keep only the 10 relevant columns
df_raw = df_raw.iloc[:, :10]
df_raw.columns = [
    "tag_no", "bw",
    "side_length", "side_breadth", "side_light", "side_temp",
    "top_length", "top_breadth", "top_light", "top_temp"
]

# ── 2. Clean numeric values (strip "cm", "°c", etc.) ─────────────────────────
def clean_num(val):
    if pd.isna(val):
        return np.nan
    val = str(val).lower()
    val = re.sub(r"[^\d.]", "", val)
    try:
        return float(val)
    except:
        return np.nan

for col in ["bw", "side_length", "side_breadth", "side_temp",
            "top_length", "top_breadth", "top_temp"]:
    df_raw[col] = df_raw[col].apply(clean_num)

# ── 3. Forward-fill tag_no and bw (they appear on first row of each group) ───
df_raw["tag_no"] = df_raw["tag_no"].ffill()
df_raw["bw"] = df_raw["bw"].ffill()

# ── 4. Drop rows with no scan data ───────────────────────────────────────────
df_raw = df_raw.dropna(subset=["side_length", "side_breadth", "side_temp",
                                 "top_length", "top_breadth", "top_temp"])

# ── 5. Compute averages per row ───────────────────────────────────────────────
df_raw["avg_length"]  = (df_raw["side_length"] + df_raw["top_length"]) / 2
df_raw["avg_breadth"] = (df_raw["side_breadth"] + df_raw["top_breadth"]) / 2
df_raw["avg_temp"]    = (df_raw["side_temp"] + df_raw["top_temp"]) / 2

# ── 6. Label health status ────────────────────────────────────────────────────
# Healthy: BW 1.2 to 3.0 kg AND avg temp 35 to 37 degrees
def label_health(row):
    bw_ok   = 1.2 <= row["bw"] <= 3.0
    temp_ok = 35.0 <= row["avg_temp"] <= 37.0
    return 1 if (bw_ok and temp_ok) else 0

df_raw["health_status"] = df_raw.apply(label_health, axis=1)

# ── 7. Build final dataset ────────────────────────────────────────────────────
df = df_raw[["bw", "avg_length", "avg_breadth", "avg_temp", "health_status"]].copy()
df = df.dropna()
df.columns = ["weight_kg", "avg_length_cm", "avg_breadth_cm", "temp_c", "health_status"]

print(f"Total records:  {len(df)}")
print(f"Healthy (1):    {df['health_status'].sum()}")
print(f"Unhealthy (0):  {(df['health_status'] == 0).sum()}")
print(df.describe())

# ── 8. Save cleaned dataset ───────────────────────────────────────────────────
df.to_csv("data/chicken_dataset_real.csv", index=False)
print("\nSaved: data/chicken_dataset_real.csv")

# ── 9. Train/test split ───────────────────────────────────────────────────────
X = df[["weight_kg", "avg_length_cm", "avg_breadth_cm", "temp_c"]]
y = df["health_status"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── 10. Train Random Forest ───────────────────────────────────────────────────
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ── 11. Evaluate ──────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
f1       = f1_score(y_test, y_pred, zero_division=0)
fn       = ((y_test == 0) & (y_pred == 1)).sum()
tp       = ((y_test == 0) & (y_pred == 0)).sum()
fer      = fn / (fn + tp) if (fn + tp) > 0 else 0.0

print("\n=== MODEL EVALUATION ===")
print(f"Accuracy:         {accuracy:.4f}")
print(f"F1 Score:         {f1:.4f}")
print(f"False Error Rate: {fer:.4f}")
print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")
print(f"\n{classification_report(y_test, y_pred, target_names=['Unhealthy','Healthy'], zero_division=0)}")

# ── 12. Save metrics ──────────────────────────────────────────────────────────
metrics = {
    "accuracy":         round(accuracy, 4),
    "f1_score":         round(f1, 4),
    "false_error_rate": round(fer, 4),
    "train_size":       len(X_train),
    "test_size":        len(X_test)
}
with open("data/model_metrics_real.json", "w") as f:
    json.dump(metrics, f, indent=2)
print("Saved: data/model_metrics_real.json")

# ── 13. Save model ────────────────────────────────────────────────────────────
with open("ml_models/chicken_health_model.pkl", "wb") as f:
    pickle.dump(model, f)
print("Saved: ml_models/chicken_health_model.pkl")

print("\nDone. Drop the new .pkl into ml_models/ and restart Flask.")