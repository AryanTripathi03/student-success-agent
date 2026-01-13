# ui/app.py
import streamlit as st
import pandas as pd
import os

import sys

# -------------------------
# Path setup
# -------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------
# Imports
# -------------------------
from agents.weak_subject_agent import WeakSubjectAgent
from agents.risk_agent import AcademicRiskAgent
from agents.study_plan_agent import StudyPlanAgent
from agents.advanced_mentorship_insight_agent import AdvancedMentorshipAgent

from services.hf_wrapper import HFGenerator

# -------------------------
# App Config
# -------------------------
st.set_page_config(
    page_title="AI Student Success Agent",
    layout="wide"
)

st.title("🎓 AI Autonomous Student Success Agent")

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    students = pd.read_csv("data/students.csv", dtype=str)
    subjects = pd.read_csv("data/subjects.csv", dtype=str)
    performance = pd.read_csv("data/performance.csv", dtype=str)

    # Clean columns
    students.columns = students.columns.str.strip()
    subjects.columns = subjects.columns.str.strip()
    performance.columns = performance.columns.str.strip()

    # Strip values
    students = students.apply(lambda x: x.str.strip())
    subjects = subjects.apply(lambda x: x.str.strip())
    performance = performance.apply(lambda x: x.str.strip())

    # Numeric safety
    performance["marks_obtained"] = pd.to_numeric(
        performance["marks_obtained"], errors="coerce"
    ).fillna(0)

    performance["max_marks"] = pd.to_numeric(
        performance.get("max_marks", 100), errors="coerce"
    ).fillna(100)

    performance["attendance"] = pd.to_numeric(
        performance.get("attendance", 0), errors="coerce"
    ).fillna(0)

    return students, subjects, performance


students, subjects, performance = load_data()

# -------------------------
# Sidebar – Student Selection
# -------------------------
st.sidebar.header("Select Student")
students["display_name"] = students["student_id"] + " - " + students["name"]
selection = st.sidebar.selectbox("Student", students["display_name"])

student_id = selection.split(" - ")[0]
student_info = students[students["student_id"] == student_id].iloc[0]

# -------------------------
# Student Profile
# -------------------------
st.subheader("👤 Student Profile")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Student ID", student_info["student_id"])
c2.metric("Name", student_info["name"])
c3.metric("Semester", student_info["current_semester"])
c4.metric("Branch", student_info["branch"])

# -------------------------
# Initialize Agents
# -------------------------
weak_agent = WeakSubjectAgent()
risk_agent = AcademicRiskAgent()
study_agent = StudyPlanAgent()
mentorship_agent = AdvancedMentorshipAgent()
hf_gen = HFGenerator()

# -------------------------
# Run Agents
# -------------------------
weak_df = weak_agent.run(performance, subjects)
risk_df = risk_agent.run(performance, subjects)
study_df = study_agent.run(weak_df)

student_weak = weak_df[weak_df["student_id"] == student_id]
student_risk = risk_df[risk_df["student_id"] == student_id]
student_plan = study_df[study_df["student_id"] == student_id]

# -------------------------
# Risk Section
# -------------------------
st.subheader("⚠️ Academic Risk Assessment")

if not student_risk.empty:
    r = student_risk.iloc[0]
    score = round(float(r["risk_score"]), 2)

    if r["risk_level"] == "High":
        st.error(f"High Risk (Score: {score})")
    elif r["risk_level"] == "Medium":
        st.warning(f"Medium Risk (Score: {score})")
    else:
        st.success(f"Low Risk (Score: {score})")
else:
    st.info("Risk data not available")

# -------------------------
# Weak Subjects
# -------------------------
st.subheader("📉 Weak Subjects")

if student_weak.empty:
    st.success("No weak subjects detected 🎉")
else:
    merged_weak = student_weak.merge(
        subjects, on="subject_id", how="left"
    )

    display_cols = ["subject_id", "name", "avg_score"]
    if "difficulty_factor" in merged_weak.columns:
        display_cols.append("difficulty_factor")

    st.dataframe(
        merged_weak[display_cols],
        width="stretch"
    )

# -------------------------
# Study Plan
# -------------------------
st.subheader("📅 Personalized Study Plan")

if student_plan.empty:
    st.info("No study plan required.")
else:
    st.dataframe(student_plan, width="stretch")

# -------------------------
# Deterministic Mentorship (Logic)
# -------------------------
st.subheader("💡 AI Mentorship Insights (Deterministic)")

logic_insights = mentorship_agent.generate_mentorship(
    student_info=student_info,
    student_risk=student_risk,
    student_weak=merged_weak if not student_weak.empty else student_weak,
    student_plan=student_plan
)

st.text_area(
    "Data-Driven Guidance",
    logic_insights,
    height=280
)



st.subheader("🧠 AI Mentor (Generative Layer)")

try:
    with st.spinner("Generating AI mentorship guidance..."):
        enhanced = hf_gen.enhance(logic_insights)

    st.text_area("AI Mentor Output", enhanced, height=300)

except Exception as e:
    st.warning(f"Generative AI unavailable: {e}")