import requests
import json
import uuid
from app.database.storeQuizDB import StoreQuizDB

MODEL_NAME = "llama3.2:latest"

database  = StoreQuizDB()
class QuizService:

    def generate_quiz(self, target_role: str):

        prompt = f"""
        You are an expert technical interviewer.

        Generate 10 multiple choice questions for the role: {target_role}.

        Rules:
        - Each question must have 4 options (A, B, C, D)
        - Mention correct option clearly
        - Return ONLY valid JSON.
        - No explanation.

        Format:

        [
          {{
            "question_text": "Question here?",
            "options": {{
              "A": "Option A text",
              "B": "Option B text",
              "C": "Option C text",
              "D": "Option D text"
            }},
            "correct_option": "A"
          }}
        ]
        """

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()
        content = result["response"]

        # Convert JSON string to Python list
        questions = json.loads(content)

        # Create unique session id
        session_id = str(uuid.uuid4())

        # Store in database
        database.save_quiz(session_id, questions)

        # we return session_id and questions (without correct answers) to frontend
        safe_questions = []
        for q in questions:
            safe_q = {
                "question_text": q["question_text"],
                "options": q["options"]
            }
            safe_questions.append(safe_q)

        return {
            "session_id": session_id,
            "questions": safe_questions
        }

    def submit_quiz(self, session_id: str, answers: list):

        questions = database.get_quiz(session_id)

        if not questions:
            return {"error": "Invalid session"}

        score = 0

        for q, ans in zip(questions, answers):
            if q["correct_option"] == ans:
                score += 1

        # remove session after submit
        del self.quiz_store[session_id]

        return {
            "score": score,
            "total": len(questions)
        }