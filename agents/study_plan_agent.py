# agents/study_plan_agent.py
import pandas as pd
from datetime import datetime, timedelta

class StudyPlanAgent:
    """
    Generates a prioritized, adaptive study plan
    based on weak subject severity.
    """

    def run(self, weak_df: pd.DataFrame) -> pd.DataFrame:
        if weak_df.empty:
            return pd.DataFrame()

        df = weak_df.copy()

        # -----------------------------
        # 1️⃣ Ensure numeric scores
        # -----------------------------
        df["avg_score"] = pd.to_numeric(
            df["avg_score"], errors="coerce"
        ).fillna(0)

        # -----------------------------
        # 2️⃣ Compute priority score
        # Lower score → higher priority
        # -----------------------------
        df["priority_score"] = 100 - df["avg_score"]

        # -----------------------------
        # 3️⃣ Generate study schedule
        # -----------------------------
        plans = []
        today = datetime.today()

        for student_id, group in df.groupby("student_id"):
            group = group.sort_values("priority_score", ascending=False)

            for i, row in enumerate(group.itertuples(), start=1):
                plans.append({
                    "student_id": student_id,
                    "subject_id": row.subject_id,
                    "focus_area": "Concept Revision + Practice",
                    "scheduled_date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "priority_score": round(row.priority_score, 2)
                })

        return pd.DataFrame(plans)
