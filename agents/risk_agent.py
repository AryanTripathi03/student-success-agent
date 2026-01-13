# agents/risk_agent.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier  # Using Random Forest for stability

class AcademicRiskAgent:
    """
    Predicts academic risk (Low, Medium, High) for students based on
    performance, attendance, and subject difficulty.
    """

    def __init__(self):
        self.model = None
        self.encoder = LabelEncoder()
        self.trained = False

    # -------------------------
    # Feature Engineering
    # -------------------------
    def prepare_features(self, df: pd.DataFrame, subjects: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for risk prediction:
        - average marks per student
        - weighted marks per student
        - average attendance
        - number of exams taken
        """
        # Ensure numeric types
        numeric_cols = ["marks_obtained", "attendance", "max_marks"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Merge with subject difficulty
        if "difficulty_factor" in subjects.columns:
            subjects["difficulty_factor"] = pd.to_numeric(subjects["difficulty_factor"], errors="coerce").fillna(1)
            df = df.merge(subjects[["subject_id", "difficulty_factor"]], on="subject_id", how="left")
        else:
            df["difficulty_factor"] = 1.0

        # Weighted marks
        df["weighted_marks"] = df["marks_obtained"] * df["difficulty_factor"]

        # Aggregate per student
        features = df.groupby("student_id").agg(
            avg_marks=("marks_obtained", "mean"),
            avg_weighted_marks=("weighted_marks", "mean"),
            avg_attendance=("attendance", "mean"),
            exams_taken=("exam_type", "count")
        ).reset_index()

        # Fill any remaining NaNs
        features = features.fillna(0)
        return features

    # -------------------------
    # Train Model
    # -------------------------
    def train_model(self, X: pd.DataFrame, y: pd.Series):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X, y)
        self.trained = True

    # -------------------------
    # Run Risk Prediction
    # -------------------------
    def run(self, performance: pd.DataFrame, subjects: pd.DataFrame) -> pd.DataFrame:
        # Prepare features
        features = self.prepare_features(performance, subjects)

        # Risk labeling (dummy example: adjust logic as per your policy)
        # Here, we label risk based on avg_marks
        risk_labels = []
        for mark in features["avg_marks"]:
            if mark >= 75:
                risk_labels.append("Low")
            elif mark >= 50:
                risk_labels.append("Medium")
            else:
                risk_labels.append("High")
        y = pd.Series(risk_labels)

        # Encode labels
        y_enc = self.encoder.fit_transform(y)

        # Train model if not trained
        if not self.trained:
            self.train_model(features.drop("student_id", axis=1), y_enc)

        # Predict risk
        y_pred_enc = self.model.predict(features.drop("student_id", axis=1))
        y_pred = self.encoder.inverse_transform(y_pred_enc)

        result = features[["student_id"]].copy()
        result["risk_level"] = y_pred
        result["risk_score"] = features["avg_marks"]  # Optional: numeric score

        return result
