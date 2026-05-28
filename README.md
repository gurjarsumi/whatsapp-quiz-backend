# SkillBytes WhatsApp-Style Quiz Application 🚀

A responsive, lightweight quiz application featuring a WhatsApp-inspired chat interface and a robust real-time analytics engine. Built using **React, FastAPI, and MongoDB Atlas**

## 📌 Project Overview
The application walks users through an intuitive, non-authenticated assessment path: **Exam Selection ➔ Subject Selection ➔ Chapter Selection ➔ Interactive Quiz Chat Thread**

### Core Features Met:
* **WhatsApp Chat Interface:** Questions flow in dynamically as system messages; multiple-choice answer options render cleanly as message interaction bubbles.
* **State Preservation:** Sequential question delivery with explicit tracking of question display timestamps, user submission timestamps, and exact response duration margins
* **Advanced Aggregation Analytics Dashboard:** Leverages native MongoDB pipeline operators to calculate system-wide metrics dynamically without overloading memory layers

---

## 📊 Database Design & Analytics Thinking

To accommodate quick navigation indexing and historical tracking, MongoDB was utilized to implement a highly scannable, document-based architecture

### Schema Architecture
* **`quiz_sessions`**: Houses user interactions, keeping an array of sub-document timestamps to isolate completion metrics and drops
  
```json
{
  "_id": "ObjectId",
  "user_id": "String",
  "chapter_id": "ObjectId",
  "started_at": "ISODate",
  "completed_at": "ISODate (Null if abandoned)",
  "responses": [
    {
      "question_id": "ObjectId",
      "selected_option": "Int",
      "is_correct": "Boolean",
      "shown_at": "ISODate",
      "submitted_at": "ISODate",
      "duration_seconds": "Float"
    }
  ]
}