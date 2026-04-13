import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

import joblib

# Load dataset
data = pd.read_csv("dataset.csv")

# 🔥 CLEAN COLUMN NAMES
data.columns = data.columns.str.strip()

print("Columns:", data.columns)

# Encode categorical columns
le_soil = LabelEncoder()
le_crop = LabelEncoder()
le_fert = LabelEncoder()

data['Soil Type'] = le_soil.fit_transform(data['Soil Type'])
data['Crop Type'] = le_crop.fit_transform(data['Crop Type'])
data['Fertilizer Name'] = le_fert.fit_transform(data['Fertilizer Name'])

# Features (INPUT)
X = data[['Temparature', 'Humidity', 'Moisture',
          'Soil Type', 'Crop Type',
          'Nitrogen', 'Potassium', 'Phosphorous']]

# Target (OUTPUT)
y = data['Fertilizer Name']

# ✅ TRAIN-TEST SPLIT (IMPORTANT ADDITION)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=200)
model.fit(X_train, y_train)

# Prediction on test data
y_pred = model.predict(X_test)

# ==============================
# ✅ EVALUATION METRICS
# ==============================

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print("\n=== Evaluation Metrics ===")
print("Accuracy :", accuracy * 100, "%")
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)

print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred))

# ==============================
# ✅ CONFUSION MATRIX
# ==============================

cm = confusion_matrix(y_test, y_pred)

plt.figure()
sns.heatmap(cm, annot=True, fmt='d')
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# ==============================
# ✅ FEATURE IMPORTANCE
# ==============================

importances = model.feature_importances_
features = X.columns

plt.figure()
plt.barh(features, importances)
plt.title("Feature Importance")
plt.xlabel("Importance Score")
plt.show()

# ==============================
# ✅ SAVE MODEL (UNCHANGED)
# ==============================

joblib.dump(model, "model.pkl")
joblib.dump(le_soil, "soil_encoder.pkl")
joblib.dump(le_crop, "crop_encoder.pkl")
joblib.dump(le_fert, "fert_encoder.pkl")

print("✅ Model & encoders saved")