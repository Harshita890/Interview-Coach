import random
import re

from models.analyzer import analyze_interview


class AIInterviewPracticeModel:
    """Local AI interviewer model for question generation and answer review."""

    def __init__(self):
        self.categories = ["HR", "Technical", "Behavioral", "Situational", "Project-Based"]
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
        self.category_bank = {
            "HR": [
                "Why should we hire you for the {role} role?",
                "What are your short-term career goals as a {role}?",
            ],
            "Technical": [
                "Explain one technical concept important for a {role} in simple terms.",
                "How do you debug a technical issue when the first solution does not work?",
            ],
            "Behavioral": [
                "Tell me about a time you received feedback and improved your work.",
                "Describe a time you had to manage pressure or a tight deadline.",
            ],
            "Situational": [
                "What would you do if you were assigned a task with unclear requirements?",
                "How would you handle a disagreement with a teammate during a project?",
            ],
            "Project-Based": [
                "Walk me through your strongest project and your personal contribution.",
                "What was the hardest part of a project you built, and how did you solve it?",
            ],
        }

    def generate_question(self, role, difficulty, category=None, resume_text=""):
        if resume_text:
            resume_question = self._resume_question(role, resume_text)
            if resume_question:
                return resume_question

        if category and category in self.category_bank:
            questions = self.category_bank[category]
        else:
            questions = self.question_bank.get(difficulty, self.question_bank["Beginner"])
        return random.choice(questions).format(role=role)

    def generate_mock_round(self, role, difficulty, resume_text=""):
        categories = self.categories
        questions = [
            self.generate_question(role, difficulty, category=category, resume_text=resume_text if category == "Project-Based" else "")
            for category in categories
        ]
        return list(zip(categories, questions))

    def generate_interview_round(self, role, difficulty, category="HR", resume_text="", count=7):
        """Build a complete interview round for the selected focus area."""
        count = max(6, min(int(count or 7), 7))
        round_questions = []

        intro_questions = [
            "Hi {name}, welcome. To begin, please introduce yourself for the {role} role.",
            "What attracted you to the {role} role, and what makes you a strong fit?",
        ]

        focus_questions = self.category_bank.get(category, self.category_bank["HR"])
        general_questions = self.question_bank.get(difficulty, self.question_bank["Beginner"])
        resume_questions = self._resume_round_questions(role, resume_text)

        if category == "Project-Based" and resume_questions:
            source_questions = resume_questions + focus_questions + general_questions
        else:
            source_questions = focus_questions + resume_questions + general_questions

        source_questions = intro_questions + source_questions

        for question in source_questions:
            formatted = question.format(role=role, name="{name}")
            if formatted not in round_questions:
                round_questions.append(formatted)
            if len(round_questions) == count:
                break

        fallback_index = 0
        while len(round_questions) < count:
            fallback = general_questions[fallback_index % len(general_questions)].format(role=role)
            if fallback not in round_questions:
                round_questions.append(fallback)
            fallback_index += 1

        return round_questions

    def review_answer(self, question, answer, candidate_name, role, difficulty, category=None, video_filename=None):
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
        next_question = self._next_question(role, difficulty, question, category)

        return {
            "candidate_name": candidate_name,
            "role": role,
            "difficulty": difficulty,
            "category": category,
            "question": question,
            "answer": answer_text,
            "video_filename": video_filename,
            "analysis": analysis,
            "model_feedback": model_feedback,
            "next_question": next_question,
        }

    def _next_question(self, role, difficulty, current_question, category=None):
        questions = self.category_bank.get(category) if category else None
        if not questions:
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

    def _resume_question(self, role, resume_text):
        keywords = self._resume_keywords(resume_text)
        if not keywords:
            return None

        topic = random.choice(keywords)
        return (
            f"Your resume mentions {topic}. Can you explain how you used it in a project "
            f"and why it matters for the {role} role?"
        )

    def _resume_round_questions(self, role, resume_text):
        keywords = self._resume_keywords(resume_text)
        if not keywords:
            return []

        questions = []
        for topic in keywords[:4]:
            questions.append(
                f"Your CV mentions {topic}. Can you explain where you used it and what result you achieved?"
            )
        questions.append(f"Which CV project best proves you are ready for the {role} role, and why?")
        questions.append("Tell me about one challenge from your CV work and how you handled it.")
        return questions

    def _resume_keywords(self, resume_text):
        common_words = {
            "and", "the", "for", "with", "from", "this", "that", "have", "about",
            "using", "work", "project", "skills", "experience", "education",
        }
        words = re.findall(r"[A-Za-z][A-Za-z+#.]{2,}", resume_text)
        keywords = []
        for word in words:
            clean = word.strip(".,:;()").lower()
            if clean not in common_words and clean not in keywords:
                keywords.append(clean)
        return [word.title() for word in keywords[:10]]
