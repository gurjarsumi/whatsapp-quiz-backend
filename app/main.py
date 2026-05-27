from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from app.database import exams_col, subjects_col, chapters_col, questions_col, sessions_col
from app.models import QuizSession, QuestionResponse

app = FastAPI(title="SkillBytes WhatsApp-Style Quiz API")

# CORS middleware to allow front-end access from any origin (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility function to convert MongoDB documents to JSON-serializable format
def serialize_doc(doc) -> dict:
    if not doc:
        return {}
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

## SECTION 1: METADATA & NAVIGATION NAVIGATION ENDPOINTS
# These endpoints provide the necessary metadata for the front-end to construct the hierarchical navigation structure.

# Fetch all exams to build the top-level navigation.
@app.get("/api/exams")
def get_exams():
    """Fetch all available exams."""
    return [serialize_doc(e) for e in exams_col.find()]

# Fetch subjects for a specific exam to build the next level of navigation.
@app.get("/api/exams/{exam_id}/subjects")
def get_subjects(exam_id: str):
    """Fetch subjects belonging to a specific exam."""
    return [serialize_doc(s) for s in subjects_col.find({"exam_id": exam_id})]

# Fetch chapters for a specific subject to build the final level of navigation before quiz initiation.
@app.get("/api/subjects/{subject_id}/chapters")
def get_chapters(subject_id: str):
    """Fetch chapters belonging to a specific subject."""
    return [serialize_doc(c) for c in chapters_col.find({"subject_id": subject_id})]

## SECTION 2: CORE QUIZ CORE FLOW ENDPOINTS (WhatsApp-Style)
# The following endpoints implement the core quiz flow in a WhatsApp-style manner, where users receive one question at a time and respond sequentially. The backend tracks precise response durations and manages quiz sessions effectively.

# Endpoint to start a new quiz session for a given user and chapter. It initializes the session and serves the first question immediately.
@app.post("/api/quiz/start")
def start_quiz(payload: dict = Body(...)):
    """
    Initializes a fresh quiz session. No login required.
    Expects: { "user_id": "str", "chapter_id": "str" }
    """
    user_id = payload.get("user_id")
    chapter_id = payload.get("chapter_id")
    
    if not user_id or not chapter_id:
        raise HTTPException(status_code=400, detail="Missing user_id or chapter_id")
    
    # Fetch all questions for this chapter to deliver them sequentially
    questions = list(questions_col.find({"chapter_id": chapter_id}))
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this chapter")
    
    # Initialize session in database with timezone-aware UTC datetime
    new_session = {
        "user_id": user_id,
        "chapter_id": chapter_id,
        "started_at": datetime.now(timezone.utc),
        "completed_at": None,
        "responses": []
    }
    session_id = str(sessions_col.insert_one(new_session).inserted_id)
    
    # Serve the very first question
    first_question = serialize_doc(questions[0])
    # Protect answer visibility from front-end inspection
    if "correct_option_index" in first_question:
        del first_question["correct_option_index"]
        
    return {
        "session_id": session_id,
        "question": first_question,
        "current_index": 0,
        "total_questions": len(questions)
    }

# Endpoint to submit an answer for the current question. It processes the answer, tracks response durations, and serves the next question in sequence. If all questions are answered, it marks the session as completed.
@app.post("/api/quiz/submit")
def submit_answer(payload: dict = Body(...)):
    """
    Processes an answer, tracks precise response durations, 
    and systematically rolls out the next question.
    """
    session_id = payload.get("session_id")
    question_id = payload.get("question_id")
    selected_option = payload.get("selected_option")
    shown_at_str = payload.get("shown_at")
    submitted_at_str = payload.get("submitted_at")

    # Parse timestamps safely by verifying they aren't None first
    try:
        if shown_at_str:
            shown_at = datetime.fromisoformat(shown_at_str.replace("Z", "+00:00"))
        else:
            shown_at = datetime.now(timezone.utc)

        if submitted_at_str:
            submitted_at = datetime.fromisoformat(submitted_at_str.replace("Z", "+00:00"))
        else:
            submitted_at = datetime.now(timezone.utc)
            
    except Exception:
        shown_at = datetime.now(timezone.utc)
        submitted_at = datetime.now(timezone.utc)

    # Calculate duration safely now that timestamps are resolved
    duration_seconds = max(0.0, (submitted_at - shown_at).total_seconds())

    # Verify session existence
    session = sessions_col.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Quiz session not found")
        
    # Verify question details and evaluate success
    question = questions_col.find_one({"_id": ObjectId(question_id)})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    # 1. Verify selected_option is present in the payload
    if selected_option is None:
        raise HTTPException(status_code=400, detail="Missing selected_option in payload")
        
    # 2. Safely evaluate correctness now that the type checker knows it's not None
    is_correct = (int(selected_option) == question["correct_option_index"])
    
    # Append response details to tracking history
    response_obj = {
        "question_id": question_id,
        "selected_option": int(selected_option),
        "is_correct": is_correct,
        "shown_at": shown_at,
        "submitted_at": submitted_at,
        "duration_seconds": round(duration_seconds, 2)
    }
    
    sessions_col.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {"responses": response_obj}}
    )
    
    # Find all questions in this chapter to evaluate what comes next
    all_questions = list(questions_col.find({"chapter_id": session["chapter_id"]}))
    answered_count = len(session["responses"]) + 1  # Including current response
    
    if answered_count >= len(all_questions):
        # All questions exhausted -> Complete quiz session with timezone-aware UTC datetime
        sessions_col.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"completed_at": datetime.now(timezone.utc)}}
        )
        return {"status": "completed", "next_question": None}
    
    # Pull next sequential question
    next_question = serialize_doc(all_questions[answered_count])
    if "correct_option_index" in next_question:
        del next_question["correct_option_index"]
        
    return {
        "status": "ongoing",
        "next_question": next_question,
        "current_index": answered_count,
        "total_questions": len(all_questions)
    }


## SECTION 3: ANALYTICS AGGREGATION DASHBOARD PIPELINES
# This endpoint computes various data-driven metrics natively via MongoDB aggregation pipelines, providing insights into user engagement, quiz performance, and behavioral patterns without the need for external analytics tools.

@app.get("/api/analytics/dashboard")
def get_analytics_dashboard():
    """
    Computes data-driven metrics natively via MongoDB aggregation pipelines.
    """
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    
    # Pipeline 1: DAU / WAU Analytics
    active_users_pipeline = [
        {"$match": {"started_at": {"$gte": seven_days_ago}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$started_at"}},
            "unique_users": {"$addToSet": "$user_id"}
        }},
        {"$project": {"date": "$_id", "count": {"$size": "$unique_users"}, "_id": 0}},
        {"$sort": {"date": 1}}
    ]
    dau_data = list(sessions_col.aggregate(active_users_pipeline))
    
    # Pipeline 2: Questions Served, Answered, and Avg Response Time
    totals_pipeline = [
        {"$unwind": "$responses"},
        {"$group": {
            "_id": None,
            "total_answered": {"$sum": 1},
            "avg_duration": {"$avg": "$responses.duration_seconds"}
        }}
    ]
    totals_res = list(sessions_col.aggregate(totals_pipeline))
    total_answered = totals_res[0]["total_answered"] if totals_res else 0
    avg_response_time = round(totals_res[0]["avg_duration"], 2) if totals_res else 0
    
    # Pipeline 3: Quiz Completion Rate
    total_sessions = sessions_col.count_documents({})
    completed_sessions = sessions_col.count_documents({"completed_at": {"$ne": None}})
    completion_rate = round((completed_sessions / total_sessions) * 100, 2) if total_sessions > 0 else 0
    
    # Pipeline 4: Peak Activity Hours Analysis
    peak_hours_pipeline = [
        {"$group": {
            "_id": {"$hour": "$started_at"},
            "session_count": {"$sum": 1}
        }},
        {"$project": {"hour": "$_id", "sessions": "$session_count", "_id": 0}},
        {"$sort": {"hour": 1}}
    ]
    peak_hours_data = list(sessions_col.aggregate(peak_hours_pipeline))
    
    # Pipeline 5: Drop-Off Analysis
    # Counts how many users dropped off at question index 1, 2, 3, etc.
    dropoff_pipeline = [
        {"$match": {"completed_at": None}},
        {"$project": {"questions_answered": {"$size": "$responses"}}},
        {"$group": {
            "_id": "$questions_answered",
            "dropoff_count": {"$sum": 1}
        }},
        {"$project": {"questions_completed_before_leaving": "$_id", "count": "$dropoff_count", "_id": 0}},
        {"$sort": {"questions_completed_before_leaving": 1}}
    ]
    dropoff_data = list(sessions_col.aggregate(dropoff_pipeline))
    
    return {
        "summary": {
            "questions_served": total_answered,  # App serves next instantly after answer
            "questions_answered": total_answered,
            "average_response_time_seconds": avg_response_time,
            "quiz_completion_rate_percentage": completion_rate
        },
        "daily_active_users": dau_data,
        "peak_activity_hours": peak_hours_data,
        "dropoff_analysis": dropoff_data
    }