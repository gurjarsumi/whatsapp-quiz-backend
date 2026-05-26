from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Hierarchy Models
class Exam(BaseModel):
    name: str
    description: Optional[str] = None

class Subject(BaseModel):
    exam_id: str
    name: str

class Chapter(BaseModel):
    subject_id: str
    name: str

class Question(BaseModel):
    chapter_id: str
    question_text: str
    options: List[str]  # e.g., ["Option A", "Option B", "Option C", "Option D"]
    correct_option_index: int  # Single correct answer (0-3) 

# Analytics & Trackers
class QuestionResponse(BaseModel):
    question_id: str
    selected_option: int
    is_correct: bool
    shown_at: datetime  # Timestamp when question appeared 
    submitted_at: datetime  # Timestamp when user clicked Next 
    duration_seconds: float  # Difference between submitted and shown 

class QuizSession(BaseModel):
    user_id: str  # Generated unique string per visitor (No Login/Signup required) 
    chapter_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None  # If null, means user dropped off 
    responses: List[QuestionResponse] = []