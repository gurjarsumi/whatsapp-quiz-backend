# SkillBytes WhatsApp-Style Quiz Application 🚀

A responsive, lightweight quiz application featuring a WhatsApp-inspired chat interface and a robust real-time analytics engine. [cite_start]Built using **React, FastAPI, and MongoDB Atlas**[cite: 3, 5, 6, 7].

## 📌 Project Overview
[cite_start]The application walks users through an intuitive, non-authenticated assessment path: **Exam Selection ➔ Subject Selection ➔ Chapter Selection ➔ Interactive Quiz Chat Thread**[cite: 8, 9, 12].

### Core Features Met:
* [cite_start]**WhatsApp Chat Interface:** Questions flow in dynamically as system messages; multiple-choice answer options render cleanly as message interaction bubbles[cite: 13, 16].
* [cite_start]**State Preservation:** Sequential question delivery with explicit tracking of question display timestamps, user submission timestamps, and exact response duration margins[cite: 14, 16, 17, 19].
* [cite_start]**Advanced Aggregation Analytics Dashboard:** Leverages native MongoDB pipeline operators to calculate system-wide metrics dynamically without overloading memory layers[cite: 20, 31].

---

## 📊 Database Design & Analytics Thinking

[cite_start]To accommodate quick navigation indexing and historical tracking, MongoDB was utilized to implement a highly scannable, document-based architecture[cite: 7, 37].

### Schema Architecture
* [cite_start]**`quiz_sessions`**: Houses user interactions, keeping an array of sub-document timestamps to isolate completion metrics and drops[cite: 18, 19, 26, 27].
  
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