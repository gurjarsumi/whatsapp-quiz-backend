import random
from datetime import datetime, timedelta
from app.database import db, exams_col, subjects_col, chapters_col, questions_col, sessions_col

def seed_database():
    # 1. Clear old data
    db.client.drop_database("quiz_db")
    print("🧹 Database wiped clean.")

    # 2. Insert Exam
    exam_id = str(exams_col.insert_one({"name": "Engineering Entrance", "description": "Prep quiz"}).inserted_id)
    
    # 3. Insert Subject
    subject_id = str(subjects_col.insert_one({"exam_id": exam_id, "name": "Physics"}).inserted_id)
    
    # 4. Insert Chapter
    chapter_id = str(chapters_col.insert_one({"subject_id": subject_id, "name": "Thermodynamics"}).inserted_id)

    # 5. Insert 5 Sample Questions
    question_ids = []
    for i in range(1, 6):
        q_doc = {
            "chapter_id": chapter_id,
            "question_text": f"This is thermodynamics sample question number {i}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_option_index": random.randint(0, 3)
        }
        question_ids.append(str(questions_col.insert_one(q_doc).inserted_id))
    print(f"📚 Seeded Exam -> Subject -> Chapter -> {len(question_ids)} Questions.")

    # 6. Generate Dummy Analytics Quiz Sessions 
    # We will simulate users over the past 7 days to give your charts data
    base_time = datetime.utcnow()
    sessions_to_insert = []

    for day_offset in range(14):  # Covers Daily & Weekly active windows
        target_date = base_time - timedelta(days=day_offset)
        
        # Simulate 5-10 users per day
        for user_idx in range(random.randint(5, 10)):
            user_id = f"user_{day_offset}_{user_idx}"
            
            # Scatter starts across random hours to mock peak hours analysis
            session_start = target_date.replace(hour=random.choice([9, 10, 14, 15, 20, 21]), minute=random.randint(0, 59))
            
            responses = []
            current_time = session_start
            
            # Decide if this user drops off early or finishes the quiz
            will_complete = random.choice([True, True, False]) # 66% completion rate
            questions_to_answer = len(question_ids) if will_complete else random.randint(1, len(question_ids) - 1)

            for idx in range(questions_to_answer):
                shown_time = current_time
                duration = random.uniform(5.0, 25.0)  # Average response time between 5-25 seconds 
                submitted_time = shown_time + timedelta(seconds=duration)
                
                responses.append({
                    "question_id": question_ids[idx],
                    "selected_option": random.randint(0, 3),
                    "is_correct": random.choice([True, False]),
                    "shown_at": shown_time,
                    "submitted_at": submitted_time,
                    "duration_seconds": round(duration, 2)
                })
                current_time = submitted_time + timedelta(seconds=2) # 2s reading gap

            session_doc = {
                "user_id": user_id,
                "chapter_id": chapter_id,
                "started_at": session_start,
                "completed_at": current_time if will_complete else None,
                "responses": responses
            }
            sessions_to_insert.append(session_doc)

    sessions_col.insert_many(sessions_to_insert)
    print(f"📊 Seeded {len(sessions_to_insert)} historical quiz sessions successfully.")

if __name__ == "__main__":
    seed_database()