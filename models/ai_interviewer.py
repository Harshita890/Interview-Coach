import random

from models.analyzer import analyze_interview


class AIInterviewPracticeModel:
    """Local AI interviewer model for question generation and answer review."""

    def __init__(self):
        self.question_bank = {
            "Beginner": [
                "Tell me about yourself and why you are interested in the {role} role.",
                "What are your strongest skills for a {role} position?",
                "Describe one project you worked on and what you learned from it.",
                "How do you handle feedback when someone reviews your work?",
            ],
            "Intermediate": [
                "Describe a challenging problem you solved while working as a {role}.",
                "Tell me about a time you worked with a team to complete a project.",
                "How would you explain a technical concept to a non-technical person?",
                "What steps do you follow when debugging an issue under time pressure?",
            ],
            "Advanced": [
                "Tell me about a project where you improved performance, quality, or reliability.",
                "Describe a time you made a technical decision and defended it with evidence.",
                "How would you design a scalable solution for a real-world product feature?",
                "Tell me about a failure, what caused it, and how you improved afterward.",
            ],
        }

    def generate_question(self, role, difficulty):
        questions = self.question_bank.get(difficulty, self.question_bank["Beginner"])
        return random.choice(questions).format(role=role)

    def review_answer(self, question, answer, candidate_name, role, difficulty, video_filename=None):
        answer_text = answer.strip()
        if not answer_text:
            answer_text = (
                "Video response submitted for AI interview practice. Add Whisper transcription "
                "to automatically convert the spoken answer into text for deeper scoring."
            )

        analysis = analyze_interview(
            transcript=answer_text,
            candidate_name=candidate_name,
            role=role,
            duration_minutes=None,
        )
        model_feedback = self._model_feedback(answer_text, analysis["metrics"]["response_quality"], video_filename)
        next_question = self._next_question(role, difficulty, question)

        return {
            "candidate_name": candidate_name,
            "role": role,
            "difficulty": difficulty,
            "question": question,
            "answer": answer_text,
            "video_filename": video_filename,
            "analysis": analysis,
            "model_feedback": model_feedback,
            "next_question": next_question,
        }

    def _next_question(self, role, difficulty, current_question):
        questions = self.question_bank.get(difficulty, self.question_bank["Beginner"])
        formatted_questions = [question.format(role=role) for question in questions]
        if current_question in formatted_questions:
            current_index = formatted_questions.index(current_question)
            return formatted_questions[(current_index + 1) % len(formatted_questions)]
        return formatted_questions[0]

    def _model_feedback(self, answer, response_quality, video_filename=None):
        lowered = answer.lower()
        feedback = []

        if video_filename:
            feedback.append("Video response received. Review your recording for posture, eye contact, clarity, and confidence.")

        if response_quality >= 75:
            feedback.append("Your answer has good detail and gives the interviewer enough context.")
        else:
            feedback.append("Add more detail using a clear example, action, and final result.")

        if not any(term in lowered for term in ["result", "impact", "improved", "achieved", "delivered"]):
            feedback.append("Mention the result or impact of your work to make the answer stronger.")

        if not any(term in lowered for term in ["i", "my", "me"]):
            feedback.append("Use ownership-focused language so your personal contribution is clear.")

        if len(answer.split()) < 45:
            feedback.append("Try to answer in 45 to 90 words for a balanced interview response.")

        return feedback
