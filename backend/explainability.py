import pandas as pd
import shap
import joblib
import matplotlib.pyplot as plt
import os

# 1. Setup Environment
os.makedirs("reports", exist_ok=True)

FEATURES = [
    "avg_hr", "rhr", "overall_score", "deep_sleep_in_minutes",
    "restlessness", "efficiency", "minutes_asleep", "minutes_awake",
    "time_in_bed", "steps", "exercise_steps", "exercise_calories", "exercise_duration"
]

# 2. Load Model and Data
model = joblib.load("models/stress_model.pkl")
df = pd.read_csv("data/final_dataset.csv")
X = df[FEATURES].fillna(df[FEATURES].median(numeric_only=True))

# 3. Initialize Explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# ---------------------------------------------------------
# A. Global Importance Plot (For Thesis: Model Reliability)
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))
# Using bar plot for clear feature ranking
shap.summary_plot(shap_values, X, plot_type="bar", show=False)
plt.title("Global Feature Importance for Stress Prediction", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("reports/global_importance.png", dpi=300)
plt.close()
print("-> Saved: reports/global_importance.png")

# ---------------------------------------------------------
# B. Local Waterfall Plot (For HCAI Demo: Individual Transparency)
# ---------------------------------------------------------
# Demonstrate with the first sample (User 0)
sample_idx = 0
# Extract SHAP values for the first sample
local_vals = explainer.shap_values(X.iloc[[sample_idx]])

# Waterfall plots require the Explanation object
explanation = shap.Explanation(
    values=local_vals[0][0], 
    base_values=explainer.expected_value[0], 
    data=X.iloc[sample_idx], 
    feature_names=FEATURES
)

plt.figure(figsize=(10, 6))
shap.plots.waterfall(explanation, show=False)
plt.title("Individual Prediction Explanation (Local Transparency)", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("reports/local_explanation.png", dpi=300)
plt.close()
print("-> Saved: reports/local_explanation.png")

print("\nProcess Complete: All reports generated in the /reports directory.")