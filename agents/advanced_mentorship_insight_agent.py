# agents/advanced_mentorship_agent.py
import pandas as pd
import numpy as np

class AdvancedMentorshipAgent:
    """
    Advanced mentorship agent that provides actionable, data-driven
    guidance based on student's academic performance, risk assessment,
    weak subjects, and study plan.
    """

    def generate_mentorship(self, student_info, student_risk, student_weak, student_plan):
        insights = []

        # -----------------------------
        # 1️⃣ Academic risk summary
        # -----------------------------
        if not student_risk.empty:
            risk_level = student_risk.iloc[0]["risk_level"]
            risk_score = round(float(student_risk.iloc[0]["risk_score"]), 2)
            insights.append(f"Academic Risk Level: {risk_level} (Score: {risk_score})")
        else:
            insights.append("Academic Risk Level: Not Available")

        # -----------------------------
        # 2️⃣ Weak subject analysis
        # -----------------------------
        if not student_weak.empty:
            df = student_weak.copy()

            # Safe numeric conversion
            df["avg_score"] = pd.to_numeric(df["avg_score"], errors="coerce").fillna(0)

            if "difficulty_factor" in df.columns:
                df["difficulty_factor"] = pd.to_numeric(
                    df["difficulty_factor"], errors="coerce"
                ).fillna(1.0)
            else:
                df["difficulty_factor"] = 1.0

            # Weighted priority score
            df["priority_score"] = df["avg_score"] * df["difficulty_factor"]
            df = df.sort_values("priority_score")

            insights.append("Priority focus subjects:")

            for _, row in df.head(3).iterrows():
                insights.append(
                    f"- {row.get('name', row['subject_id'])}: "
                    f"Avg {round(row['avg_score'],1)}, "
                    f"Difficulty {row['difficulty_factor']}"
                )
        else:
            insights.append("No weak subjects detected. Maintain current performance.")

        # -----------------------------
        # 3️⃣ Study plan summary
        # -----------------------------
        if not student_plan.empty:
            upcoming = student_plan.sort_values("scheduled_date").head(5)
            insights.append("Upcoming study focus:")
            for _, row in upcoming.iterrows():
                insights.append(f"- {row['subject_id']} on {row['scheduled_date']}")
        else:
            insights.append("No immediate study plan required.")

        # -----------------------------
        # 4️⃣ Performance trend (math-based)
        # -----------------------------
        if not student_weak.empty and len(student_weak) > 1:
            scores = df["avg_score"].values
            x = np.arange(len(scores))
            slope = np.polyfit(x, scores, 1)[0]

            if slope > 0:
                insights.append("Performance trend: Improving 📈")
            elif slope < 0:
                insights.append("Performance trend: Declining 📉")
            else:
                insights.append("Performance trend: Stable ➖")

        # -----------------------------
        # 5️⃣ Improvement strategy
        # -----------------------------
        if not student_risk.empty:
            if risk_level == "High":
                insights.append(
                    "Strategy: Daily revision, reduce backlog, focus on fundamentals."
                )
            elif risk_level == "Medium":
                insights.append(
                    "Strategy: Strengthen weak subjects to move into Low Risk."
                )
            else:
                insights.append(
                    "Strategy: Maintain consistency and aim for excellence."
                )

        return "\n".join(insights)
