# Interview Mirror

## AI-Based Interview Practice Platform

Interview Mirror is an AI-powered interview practice and performance analysis platform. It helps candidates practice interview answers, analyze communication quality, measure confidence signals, detect filler words, understand sentiment, and receive personalized feedback for improvement.

The project also includes a **Video-Based AI Interviewer Practice Model** where the AI asks role-based interview questions, accepts the candidate's recorded video response, reviews the response, gives a practice score, and suggests how to improve the next answer.


## Project Overview

Preparing for interviews can be difficult without proper feedback. Interview Mirror works like a virtual interview coach by analyzing recorded or written interview responses and generating useful performance insights.

This project is designed for students, job seekers, and professionals who want to improve their interview communication, reduce hesitation, and build confidence before real interviews.

## Key Features

### Video-Based AI Interview Practice

- Provides a platform for practicing interview responses.
- AI interviewer asks role-based questions.
- Candidate can record or upload a video interview answer directly in the app.
- AI model reviews the answer and gives performance feedback.
- Helps users evaluate answers before real interviews.
- Gives improvement suggestions based on response quality.

### Speech-to-Text Conversion

- Supports interview recording upload.
- Can be extended with Whisper for automatic transcription.

### Communication Analysis

- Measures speaking speed.
- Detects filler words such as:
  - Umm
  - Uh
  - Like
  - You know

### Confidence Assessment

- Estimates confidence level using response clarity and hesitation signals.
- Highlights areas where the candidate can sound more confident.

### Sentiment Analysis

- Identifies positive, neutral, and negative tone.
- Evaluates emotional quality of interview responses.

### Interview Scoring

- Generates an overall interview performance score.
- Provides category-wise scores for confidence, communication, sentiment, and response quality.

### Personalized Feedback

- Highlights strengths.
- Identifies improvement areas.
- Gives actionable recommendations.

### Performance Dashboard

- Displays interview metrics visually.
- Shows confidence, communication, sentiment, speech pace, and filler-word count.

## Technology Stack

### Frontend

- HTML
- CSS
- JavaScript
- Bootstrap
- Chart.js

### Backend

- Python
- Flask

### AI and Machine Learning

- Rule-based NLP analysis in the current version
- Scikit-learn, NLTK, Transformers, and Whisper can be added for advanced analysis

### Database

- SQLite or MySQL can be integrated for storing user history and interview reports

## System Workflow

1. User uploads an interview recording or enters a transcript.
2. The system processes the interview response.
3. Communication metrics are calculated.
4. Filler words, sentiment, confidence, and response quality are analyzed.
5. Overall interview score is generated.
6. Dashboard displays feedback and recommendations.

## Video-Based AI Interviewer Practice Model

The AI interviewer practice model is available at `/practice`. It works as a mock interview space where a candidate selects a role and difficulty level, receives an AI-generated interview question, records or uploads a video answer, and gets instant performance feedback.

The current model is rule-based so the project can run without an external API key. It can later be upgraded with Whisper for automatic video transcription and OpenAI, Transformers, or another LLM for more advanced question generation and feedback.

## Project Objectives

- Create an AI-based interview practice platform.
- Improve interview preparation.
- Provide objective performance feedback.
- Help candidates improve communication skills.
- Reduce interview anxiety through repeated practice.
- Deliver data-driven interview improvement suggestions.

## Future Enhancements

- Real-time interview practice.
- AI-generated mock interview questions.
- Whisper-based automatic speech-to-text.
- Facial expression recognition.
- Eye contact tracking.
- Emotion detection.
- Resume analysis integration.
- User login and interview history.
- Multilingual interview support.

## Installation

```bash
git clone https://github.com/Harshita890/Interview-Coach.git
cd Interview-Coach
pip install -r requirements.txt
python app.py
```

Open the app in your browser:

```text
http://127.0.0.1:5000
```

AI interview practice page:

```text
http://127.0.0.1:5000/practice
```

## Project Structure

```plaintext
Interview-Coach/
|
|-- app.py
|-- models/
|   |-- analyzer.py
|   |-- ai_interviewer.py
|-- dataset/
|   |-- .gitkeep
|-- static/
|   |-- css/
|   |   |-- style.css
|   |-- js/
|       |-- dashboard.js
|       |-- video_practice.js
|-- templates/
|   |-- index.html
|   |-- dashboard.html
|   |-- practice.html
|-- uploads/
|   |-- .gitkeep
|-- notebooks/
|   |-- .gitkeep
|-- requirements.txt
|-- .gitignore
`-- README.md
```

## Expected Outcomes

- Better interview readiness.
- Improved communication confidence.
- Personalized learning experience.
- Data-driven interview improvement strategies.
- A practical AI-based interview practice platform for career preparation.

## Author

**Harshita Gautam**

Final Year Student | Python Developer | Machine Learning Enthusiast

---

Interview Mirror transforms interview practice into a data-driven learning experience by combining Artificial Intelligence, Natural Language Processing, and Speech Analytics to help candidates perform better in real-world interviews.
