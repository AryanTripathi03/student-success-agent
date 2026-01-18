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

from services.ollama_wrapper import OllamaGenerator

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
ollama_gen = OllamaGenerator()
# -------------------------
# Cache function for roadmap per student
# -------------------------
@st.cache_data(show_spinner=False)
def generate_roadmap(student_id, student_weak, student_plan, student_risk):
    roadmap_prompt = f"""
You are an expert academic mentor.

Create a concise, actionable roadmap for the student to achieve their priority score. 
Use the following data:

- Weak subjects: {student_weak.to_dict(orient='records')}
- Personalized study plan: {student_plan.to_dict(orient='records')}
- Current academic risk: {student_risk.to_dict(orient='records')}

Output the roadmap as:
1. Step-by-step actions
2. Weekly goals
3. Motivation tips
4. Focus areas for weak subjects
Keep it under 300 words and actionable.
"""
    return ollama_gen.enhance(roadmap_prompt)

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
    height=320
)



# -------------------------
# Initialize session state caches if not present
# -------------------------
if 'ai_outputs' not in st.session_state:
    st.session_state['ai_outputs'] = {}  # stores AI mentor outputs per student_id
if 'roadmaps' not in st.session_state:
    st.session_state['roadmaps'] = {}   # stores roadmap outputs per student_id

# -------------------------
# Side-by-side AI Sections
# -------------------------
st.subheader("🧠 AI Mentor & 🗺️ Roadmap")
col1, col2 = st.columns(2)

## -------------------------
# Left column: AI Mentor
# -------------------------
with col1:
    if st.button("Generate AI Mentorship Guidance", key=f"ai_mentor_{student_id}"):
        with st.spinner("Generating AI mentorship guidance..."):
            raw_ai = ollama_gen.enhance(
                f"""
You are an expert academic mentor.

Rewrite the mentorship advice below in:
- clear bullet points
- maximum 400 words
- actionable steps
- motivational but concise tone

Mentorship Data:
{logic_insights}
"""
            )

            # Format spacing cleanly
            st.session_state['ai_outputs'][student_id] = "\n\n".join(
                line.strip() for line in raw_ai.splitlines() if line.strip()
            )

    # Show AI text only if generated
    ai_text = st.session_state['ai_outputs'].get(student_id, "")
    if ai_text:  # only display if there is content
        st.text_area("🧠 AI Mentor Output", ai_text, height=520)

# -------------------------
# Right column: Roadmap
# -------------------------
with col2:
    if st.button("Generate Roadmap", key=f"roadmap_{student_id}"):
        with st.spinner("Creating personalized roadmap..."):
            raw_roadmap = generate_roadmap(
                student_id, student_weak, student_plan, student_risk
            )

            # Format spacing cleanly
            st.session_state['roadmaps'][student_id] = "\n\n".join(
                line.strip() for line in raw_roadmap.splitlines() if line.strip()
            )

    # Show roadmap only if generated
    roadmap_text = st.session_state['roadmaps'].get(student_id, "")
    if roadmap_text:  # only display if there is content
        st.text_area("🗺️ Personalized Roadmap", roadmap_text, height=520)
