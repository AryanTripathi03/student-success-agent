# generate_data.py
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os

# -------------------------
# Setup
# -------------------------
fake = Faker()

# Create data folder if it doesn't exist
data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# -------------------------
# 1. Students Table
# -------------------------
num_students = 5000
students = pd.DataFrame({
    "student_id": [f"S{i:05}" for i in range(1, num_students + 1)],
    "name": [fake.name() for _ in range(num_students)],  # ✅ Proper names
    "current_semester": [random.randint(1, 8) for _ in range(num_students)],
    "branch": [random.choice(["CE", "IT", "ME", "EE", "EXTC"]) for _ in range(num_students)]
})

# Strip spaces just in case
students.columns = students.columns.str.strip()
students["student_id"] = students["student_id"].astype(str).str.strip()
students["name"] = students["name"].astype(str).str.strip()

# Save students CSV
students.to_csv(os.path.join(data_folder, "students.csv"), index=False)

# -------------------------
# 2. Subjects Table
# -------------------------
subjects = pd.DataFrame({
    "subject_id": [f"SUB{i:03}" for i in range(1, 11)],
    "name": [
        "Applied Maths I", "Physics I", "Chemistry I",
        "Applied Maths II", "Physics II", "Engineering Mechanics",
        "Basic Electrical", "Programming", "Workshop", "Communication Skills"
    ],
    "semester": [1, 1, 1, 2, 2, 2, 2, 1, 1, 1],
    "branch": ["CE", "CE", "CE", "CE", "CE", "CE", "CE", "IT", "ME", "EE"],
    "credits": [4, 4, 3, 4, 4, 3, 3, 4, 2, 2],
    "difficulty_factor": [0.8, 0.7, 0.6, 0.8, 0.7, 0.7, 0.6, 0.7, 0.5, 0.5]
})

# Strip spaces
subjects.columns = subjects.columns.str.strip()
subjects["subject_id"] = subjects["subject_id"].astype(str).str.strip()

# Save subjects CSV
subjects.to_csv(os.path.join(data_folder, "subjects.csv"), index=False)

# -------------------------
# 3. Student Performance Table
# -------------------------
performance_records = []

for student in students.itertuples(index=False):
    for subject in subjects.itertuples(index=False):
        performance_records.append({
            "student_id": student.student_id,
            "subject_id": subject.subject_id,
            "exam_type": random.choice(["IA1", "IA2", "EndSem", "Lab"]),
            "marks_obtained": random.randint(30, 90),
            "max_marks": 100,
            "attendance": random.randint(60, 100),
            "exam_date": (datetime.today() + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
        })

performance = pd.DataFrame(performance_records)

# Strip spaces
performance.columns = performance.columns.str.strip()
performance["student_id"] = performance["student_id"].astype(str).str.strip()
performance["subject_id"] = performance["subject_id"].astype(str).str.strip()

# Save performance CSV
performance.to_csv(os.path.join(data_folder, "performance.csv"), index=False)

# -------------------------
# Done
# -------------------------
print("CSV files generated successfully in the 'data/' folder!")
print("Students:", students.shape)
print("Subjects:", subjects.shape)
print("Performance records:", performance.shape)
