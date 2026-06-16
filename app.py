from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from models.analyzer import analyze_interview
from models.ai_interviewer import AIInterviewPracticeModel


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "webm", "mp4", "mov"}


app = Flask(__name__)
app.config["SECRET_KEY"] = "interview-mirror-dev-key"
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

UPLOAD_DIR.mkdir(exist_ok=True)
interview_model = AIInterviewPracticeModel()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        candidate_name = request.form.get("candidate_name", "").strip() or "Candidate"
        role = request.form.get("role", "").strip() or "General Interview"
        transcript = request.form.get("transcript", "").strip()
        duration_text = request.form.get("duration", "").strip()
        recording = request.files.get("recording")
        saved_filename = None

        try:
            duration_minutes = float(duration_text) if duration_text else None
        except ValueError:
            duration_minutes = None

        if recording and recording.filename:
            if not allowed_file(recording.filename):
                flash("Please upload an audio or video file in a supported format.", "danger")
                return redirect(url_for("index"))

            original_name = secure_filename(recording.filename)
            saved_filename = f"{uuid4().hex}_{original_name}"
            recording.save(app.config["UPLOAD_FOLDER"] / saved_filename)

        if not transcript and not saved_filename:
            flash("Add a transcript or upload a recording to analyze.", "warning")
            return redirect(url_for("index"))

        result = analyze_interview(
            transcript=transcript,
            candidate_name=candidate_name,
            role=role,
            duration_minutes=duration_minutes,
            recording_name=saved_filename,
        )
        session["analysis"] = result
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    analysis = session.get("analysis")
    if not analysis:
        flash("Submit an interview response first to view the dashboard.", "info")
        return redirect(url_for("index"))

    return render_template("dashboard.html", analysis=analysis)


@app.route("/practice", methods=["GET", "POST"])
def practice():
    if request.method == "POST":
        candidate_name = request.form.get("candidate_name", "").strip() or "Candidate"
        role = request.form.get("role", "").strip() or "General Interview"
        difficulty = request.form.get("difficulty", "Beginner")
        question = request.form.get("question", "").strip()
        answer = request.form.get("answer", "").strip()

        if not question:
            question = interview_model.generate_question(role=role, difficulty=difficulty)

        if not answer:
            flash("Write your answer so the AI interviewer can review it.", "warning")
            return render_template(
                "practice.html",
                candidate_name=candidate_name,
                role=role,
                difficulty=difficulty,
                question=question,
            )

        practice_result = interview_model.review_answer(
            question=question,
            answer=answer,
            candidate_name=candidate_name,
            role=role,
            difficulty=difficulty,
        )
        return render_template("practice.html", result=practice_result)

    starter_question = interview_model.generate_question(
        role="Python Developer",
        difficulty="Beginner",
    )
    return render_template(
        "practice.html",
        candidate_name="Harshita Gautam",
        role="Python Developer",
        difficulty="Beginner",
        question=starter_question,
    )


@app.route("/reset")
def reset():
    session.pop("analysis", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
