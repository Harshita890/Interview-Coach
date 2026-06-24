# Interview Mirror 

Interview Mirror is a Python Flask web application for interview practice and response analysis. It helps candidates rehearse interview answers, record practice responses, and review feedback through a simple dashboard.

This project is lightweight and beginner friendly. It runs locally with Python and does not require an external AI API key, database, login system, Whisper transcription, or face tracking.

## Live Demo

Deployment link coming soon.

## Screenshot

App screenshot coming soon.

## Features

- Python Flask backend
- Live interview practice page at `/practice`
- Role and difficulty based interview questions
- Browser voice prompt for questions
- Camera and microphone recording in supported browsers
- Optional browser speech-to-text notes
- Rule-based answer feedback with score, strengths, and improvement tips
- Transcript or recording upload analysis
- Dashboard for confidence, communication, sentiment, pace, filler words, and response quality
- Render-ready deployment files

## Tech Stack

- Python
- Flask
- Werkzeug
- Gunicorn
- HTML templates
- CSS
- JavaScript
- Bootstrap
- Chart.js

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

## Environment Variables

Create a local `.env` file or set these variables in your hosting dashboard:

```env
SECRET_KEY=change-this-to-a-long-random-value
FLASK_DEBUG=0
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask app:

```bash
python app.py
```

Open the app:

```text
http://127.0.0.1:5000
```

Open the live practice page:

```text
http://127.0.0.1:5000/practice
```

## How It Works

1. Enter the candidate name, role, and difficulty.
2. Start a live interview session.
3. The browser speaks an interview question.
4. The candidate records an answer using camera and microphone.
5. The app reviews the transcript or recording details.
6. The dashboard shows feedback and performance metrics.

## Deployment

This app can be deployed on Python web hosting platforms such as Render, Railway, or a VPS.

Render settings:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

Set a production secret key:

```text
SECRET_KEY=choose-a-long-random-value
```

Camera, microphone, speech recognition, and speech playback work best on HTTPS.

## GitHub Language Note

This repository is a Python project. The `templates/` and `static/` folders contain support files for the Flask UI, so `.gitattributes` is used to keep GitHub's language bar focused on the Python backend.

## Future Improvements

- LLM-backed interview question generation
- Speech-to-text transcription for uploaded recordings
- User login and saved interview history
- Resume-based interview questions
- Multilingual practice
- More detailed video and audio coaching

## Author

Harshita Gautam

## License

This project is licensed under the MIT License.
