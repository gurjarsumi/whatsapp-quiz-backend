import os
from pymongo import MongoClient

MONGO_DETAILS = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = MongoClient(MONGO_DETAILS)
db = client.quiz_db

# Helper to access collections quickly
exams_col = db.get_collection("exams")
subjects_col = db.get_collection("subjects")
chapters_col = db.get_collection("chapters")
questions_col = db.get_collection("questions")
sessions_col = db.get_collection("quiz_sessions")