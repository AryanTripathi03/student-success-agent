# agents/weak_subject_agent.py
import pandas as pd

class WeakSubjectAgent:
    """
    Identifies weak subjects per student using normalized performance scores.
    """

    def run(self, performance: pd.DataFrame, subjects: pd.DataFrame) -> pd.DataFrame:
        df = performance.copy()

        # -----------------------------
        # 1️⃣ Ensure numeric columns
        # -----------------------------
        df["marks_obtained"] = pd.to_numeric(
            df["marks_obtained"], errors="coerce"
        ).fillna(0)

        df["max_marks"] = pd.to_numeric(
            df["max_marks"], errors="coerce"
        ).replace(0, 100).fillna(100)

        # -----------------------------
        # 2️⃣ Normalized score
        # -----------------------------
        df["normalized_score"] = df["marks_obtained"] / df["max_marks"]

        # -----------------------------
        # 3️⃣ Average score per subject
        # -----------------------------
        avg_scores = (
            df.groupby(["student_id", "subject_id"])["normalized_score"]
            .mean()
            .reset_index()
        )

        avg_scores["avg_score"] = (avg_scores["normalized_score"] * 100).round(2)
        avg_scores.drop(columns=["normalized_score"], inplace=True)

        # -----------------------------
        # 4️⃣ Identify weak subjects
        # -----------------------------
        weak_subjects = avg_scores[avg_scores["avg_score"] < 60]

        return weak_subjects
