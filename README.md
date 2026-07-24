# Interview Coach

Interview Coach is a Python Flask web application for interview practice and response analysis. It helps candidates rehearse interview answers, record practice responses, and review feedback through a simple dashboard.

This project is lightweight and beginner friendly. It runs locally with Python, uses SQLite for saved interview history, and does not require an external AI API key, Whisper transcription, or face tracking.

## Live Demo

Deployment link coming soon

## Screenshot

App screenshot coming soon

## Features

- Python Flask backend
- Live interview practice page at `/practice`
- Role and difficulty based interview questions
- Browser voice prompt for questions
- Camera and microphone recording in supported browsers
- Optional browser speech-to-text notes
- Rule-based answer feedback with score, strengths, and improvement tips
- Transcript or recording upload analysis
- SQLite database for saved interview sessions
- Lightweight login and account creation
- Interview history with progress trend chart
- Resume or project highlights for tailored questions
- HR, technical, behavioral, situational, and project-based categories
- Five-question mock interview round
- Stronger answer direction after each response
- Printable report that can be saved as a PDF
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
|   |-- database.py
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
|   |-- history.html
|   |-- index.html
|   |-- login.html
|   |-- report.html
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
2. Choose a category or add resume/project highlights.
3. Start a live interview session or review the five-question mock round.
4. The browser speaks an interview question.
5. The candidate records an answer using camera and microphone.
6. The app reviews the transcript or recording details.
7. The dashboard shows feedback, a stronger answer direction, and performance metrics.
8. The SQLite history page saves reports and shows score progress over time.
9. Open a saved report and use the browser print dialog to save it as a PDF.

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
- Multilingual practice
- More detailed video and audio coaching

## Author

Harshita Gautam

## License

This project is licensed under the MIT License.
