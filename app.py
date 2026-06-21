import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename

from models.analyzer import analyze_interview
from models.ai_interviewer import AIInterviewPracticeModel
from models.site_content import DIFFICULTIES, HOME_CONTENT, PRACTICE_DEFAULTS, SAMPLE_TRANSCRIPTS, get_sample_transcript


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "webm", "mp4", "mov"}


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "interview-mirror-dev-key")
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

UPLOAD_DIR.mkdir(exist_ok=True)
interview_model = AIInterviewPracticeModel()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_recording(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    original_name = secure_filename(file_storage.filename)
    saved_filename = f"{uuid4().hex}_{original_name}"
    file_storage.save(app.config["UPLOAD_FOLDER"] / saved_filename)
    return saved_filename


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

            saved_filename = save_recording(recording)

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

    return render_template("index.html", home=HOME_CONTENT, sample_keys=SAMPLE_TRANSCRIPTS.keys())


@app.route("/dashboard")
def dashboard():
    analysis = session.get("analysis")
    if not analysis:
        flash("Submit an interview response first to view the dashboard.", "info")
        return redirect(url_for("index"))

    return render_template("dashboard.html", analysis=analysis)


@app.route("/practice", methods=["GET", "POST"])
def practice():
    practice_context = {
        "difficulties": DIFFICULTIES,
        "defaults": PRACTICE_DEFAULTS,
    }

    if request.method == "POST":
        candidate_name = request.form.get("candidate_name", "").strip() or "Candidate"
        role = request.form.get("role", "").strip() or "General Interview"
        difficulty = request.form.get("difficulty", "Beginner")
        question = request.form.get("question", "").strip()
        transcript = request.form.get("transcript", "").strip()
        video_response = request.files.get("video_response")
        saved_video = save_recording(video_response)

        if not question:
            question = interview_model.generate_question(role=role, difficulty=difficulty)

        if not saved_video and not transcript:
            flash("Record or upload a video response before submitting to the AI interviewer.", "warning")
            return render_template(
                "practice.html",
                **practice_context,
                candidate_name=candidate_name,
                role=role,
                difficulty=difficulty,
                question=question,
            )

        practice_result = interview_model.review_answer(
            question=question,
            answer=transcript,
            candidate_name=candidate_name,
            role=role,
            difficulty=difficulty,
            video_filename=saved_video,
        )
        return render_template("practice.html", result=practice_result, **practice_context)

    starter_question = interview_model.generate_question(
        role=PRACTICE_DEFAULTS["role"],
        difficulty=PRACTICE_DEFAULTS["difficulty"],
    )
    return render_template(
        "practice.html",
        **practice_context,
        candidate_name=PRACTICE_DEFAULTS["candidate_name"],
        role=PRACTICE_DEFAULTS["role"],
        difficulty=PRACTICE_DEFAULTS["difficulty"],
        question=starter_question,
    )


@app.route("/practice/question")
def practice_question():
    role = request.args.get("role", "General Interview").strip() or "General Interview"
    difficulty = request.args.get("difficulty", "Beginner").strip() or "Beginner"
    return jsonify(
        {
            "question": interview_model.generate_question(role=role, difficulty=difficulty),
            "role": role,
            "difficulty": difficulty,
        }
    )


@app.route("/sample-answer/<sample_key>")
def sample_answer(sample_key):
    return jsonify({"transcript": get_sample_transcript(sample_key)})


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/reset")
def reset():
    session.pop("analysis", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
