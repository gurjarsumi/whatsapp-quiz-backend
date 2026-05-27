import random
from datetime import datetime, timedelta
from app.database import db, exams_col, subjects_col, chapters_col, questions_col, sessions_col

def seed_database():
    # 1. Clear old data inside collections safely without dropping the database
    exams_col.delete_many({})
    subjects_col.delete_many({})
    chapters_col.delete_many({})
    questions_col.delete_many({})
    sessions_col.delete_many({})
    print("🧹 Collections wiped clean safely on MongoDB Atlas.")

    # 2. Insert Mock Exam Hierarchy
    exam_id = str(exams_col.insert_one({
        "name": "Engineering Entrance Examination", 
        "description": "Comprehensive evaluation tracker for engineering candidates."
    }).inserted_id)
    
    # 3. Insert Mock Subject
    subject_id = str(subjects_col.insert_one({
        "exam_id": exam_id, 
        "name": "Physics"
    }).inserted_id)
    
    # 4. Insert Mock Chapter
    chapter_id = str(chapters_col.insert_one({
        "subject_id": subject_id, 
        "name": "Thermodynamics"
    }).inserted_id)

    # 5. Insert 5 Sequential Sample Multiple-Choice Questions
    question_ids = []
    questions_pool = [
        "What is the first law of thermodynamics primarily concerned with?",
        "In an isothermal process, which of the following variables remains strictly constant?",
        "Which thermodynamic cycle establishes the absolute upper limit for heat engine efficiency?",
        "An ideal gas undergoes an isobaric expansion. What does this indicate about the system pressure?",
        "What does a net entropy increase across an isolated system definitively signal?"
    ]
    
    options_pool = [
        ["Conservation of energy", "Conservation of mass", "Direction of heat flow", "Absolute zero limits"],
        ["Temperature", "Pressure", "Volume", "Total internal enthalpy"],
        ["Carnot Cycle", "Rankine Cycle", "Diesel Cycle", "Otto Cycle"],
        ["It remains constant", "It doubles sequentially", "It drops exponentially", "It matches atmospheric zero"],
        ["An irreversible process", "A perfectly reversible process", "An isothermal equilibrium", "Zero work output"]
    ]

    for i in range(5):
        q_doc = {
            "chapter_id": chapter_id,
            "question_text": questions_pool[i],
            "options": options_pool[i],
            "correct_option_index": random.randint(0, 3)
        }
        question_ids.append(str(questions_col.insert_one(q_doc).inserted_id))
    print(f"📚 Seeded Exam -> Subject -> Chapter -> {len(question_ids)} Core Questions.")

    # 6. Generate Dummy Analytics Quiz Sessions over a 14-Day Timeline Window
    base_time = datetime.utcnow()
    sessions_to_insert = []

    for day_offset in range(14):  
        target_date = base_time - timedelta(days=day_offset)
        
        # Simulate a randomized group of 5 to 10 unique user sessions per day
        for user_idx in range(random.randint(5, 10)):
            user_id = f"user_gen_{day_offset}_{user_idx}"
            
            # Scatter initiation times across specific hours to mock peak load periods
            selected_hour = random.choice([9, 10, 14, 15, 20, 21])
            session_start = target_date.replace(
                hour=selected_hour, 
                minute=random.randint(0, 59), 
                second=random.randint(0, 59),
                microsecond=0
            )
            
            responses = []
            current_time = session_start
            
            # Formulate completion distributions (roughly 70% finish, 30% drop off early)
            will_complete = random.random() < 0.70
            questions_to_answer = len(question_ids) if will_complete else random.randint(1, len(question_ids) - 1)

            for idx in range(questions_to_answer):
                shown_time = current_time
                duration = random.uniform(4.0, 22.0)  # Simulates active consideration time
                submitted_time = shown_time + timedelta(seconds=duration)
                
                responses.append({
                    "question_id": question_ids[idx],
                    "selected_option": random.randint(0, 3),
                    "is_correct": random.choice([True, False]),
                    "shown_at": shown_time,
                    "submitted_at": submitted_time,
                    "duration_seconds": round(duration, 2)
                })
                # Simulate a small reading pause before the next prompt displays
                current_time = submitted_time + timedelta(seconds=2) 

            session_doc = {
                "user_id": user_id,
                "chapter_id": chapter_id,
                "started_at": session_start,
                "completed_at": current_time if will_complete else None,
                "responses": responses
            }
            sessions_to_insert.append(session_doc)

    if sessions_to_insert:
        sessions_col.insert_many(sessions_to_insert)
        print(f"📊 Successfully seeded {len(sessions_to_insert)} historical mock quiz sessions directly to the cloud dashboard.")
    else:
        print("⚠️ No session documentation compiled.")

if __name__ == "__main__":
    seed_database()