# Interview Mirror

Interview Mirror is a Flask web app for interview practice and response analysis. It includes a live AI-style practice page where the browser speaks an interview question aloud, records the candidate on camera, captures spoken answer notes when browser speech recognition is available, and gives rule-based feedback after submission.

The current project is intentionally local and lightweight. It does not require an external AI API key, database, Whisper transcription, face tracking, or user accounts.

## Current Features

- Live interview practice at `/practice`
- Browser voice prompt for interview questions
- Role and difficulty based question selection
- Camera and microphone recording in supported browsers
- Optional live speech-to-text notes using browser speech recognition
- Rule-based answer review with score, strengths, and improvement tips
- Transcript or recording upload analysis from the home page
- Dashboard with confidence, communication, sentiment, pace, filler-word, and response-quality metrics
- Render-compatible deployment files

## How the AI Practice Flow Works

1. Open `/practice`.
2. Enter the candidate name, target role, and difficulty.
3. Select **Start Live Interview**.
4. The browser asks a fresh interview question aloud.
5. After the spoken question finishes, recording starts.
6. The candidate answers by speaking on camera.
7. Browser speech recognition writes answer notes when supported.
8. Submit the response to receive practice feedback and the next question.

Browsers require a user action before playing speech, so the AI voice starts after the candidate clicks the live interview button.

## Tech Stack

- Python
- Flask
- HTML
- CSS
- JavaScript
- Bootstrap
- Chart.js
- Browser MediaRecorder API
- Browser SpeechSynthesis API
- Browser SpeechRecognition API where supported

## Project Structure

```text
.
|-- app.py
|-- models/
|   |-- analyzer.py
|   |-- ai_interviewer.py
|   `-- site_content.py
|-- static/
|   |-- css/
|   |   `-- style.css
|   `-- js/
|       |-- dashboard.js
|       |-- home.js
|       `-- video_practice.js
|-- templates/
|   |-- dashboard.html
|   |-- index.html
|   `-- practice.html
|-- uploads/
|   `-- .gitkeep
|-- Procfile
|-- render.yaml
|-- requirements.txt
`-- README.md
```

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

AI practice page:

```text
http://127.0.0.1:5000/practice
```

## Deploy

This app can be deployed to Python web hosts such as Render, Railway, or a VPS.

For Render, use:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

Set a production secret:

```text
SECRET_KEY=choose-a-long-random-value
```

Camera, microphone, speech recognition, and speech playback work best on secure origins. Public deployments should use HTTPS.

## Future Improvements

- Real LLM-backed question generation and feedback
- Whisper or another speech-to-text model for uploaded recordings
- User login and saved interview history
- Resume-based interview questions
- Multilingual practice
- More detailed video and audio coaching

## Author

Harshita Gautam
