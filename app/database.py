import os
from pymongo import MongoClient

MONGO_DETAILS = "mongodb+srv://quizuser:Password123@cluster0.1lm4vjr.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_DETAILS)
db = client.quiz_db

# Helper to access collections quickly
exams_col = db.get_collection("exams")
subjects_col = db.get_collection("subjects")
chapters_col = db.get_collection("chapters")
questions_col = db.get_collection("questions")
sessions_col = db.get_collection("quiz_sessions")