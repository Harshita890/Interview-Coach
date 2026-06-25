import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename

from models.analyzer import analyze_interview
from models.ai_interviewer import AIInterviewPracticeModel
from models.database import (
    create_user,
    get_interview_session,
    init_db,
    list_interview_sessions,
    save_interview_session,
    verify_user,
)
from models.site_content import DIFFICULTIES, HOME_CONTENT, PRACTICE_DEFAULTS, SAMPLE_TRANSCRIPTS, get_sample_transcript


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "webm", "mp4", "mov"}
RESUME_EXTENSIONS = {"txt", "md"}


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "interview-mirror-dev-key")
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

UPLOAD_DIR.mkdir(exist_ok=True)
init_db()
interview_model = AIInterviewPracticeModel()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def current_user_id():
    return session.get("user_id")


@app.context_processor
def inject_user():
    return {"current_user": session.get("user")}


def allowed_resume(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in RESUME_EXTENSIONS


def read_resume_text(file_storage):
    if not file_storage or not file_storage.filename:
        return ""

    if not allowed_resume(file_storage.filename):
        return ""

    return file_storage.read().decode("utf-8", errors="ignore")[:5000]


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
        session_id = save_interview_session(result, user_id=current_user_id())
        result["session_id"] = session_id
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
        "categories": interview_model.categories,
        "defaults": PRACTICE_DEFAULTS,
    }

    if request.method == "POST":
        candidate_name = request.form.get("candidate_name", "").strip() or "Candidate"
        role = request.form.get("role", "").strip() or "General Interview"
        difficulty = request.form.get("difficulty", "Beginner")
        category = request.form.get("category", "HR")
        question = request.form.get("question", "").strip()
        transcript = request.form.get("transcript", "").strip()
        resume_text = request.form.get("resume_text", "").strip()
        resume_file = request.files.get("resume")
        video_response = request.files.get("video_response")
        saved_video = save_recording(video_response)
        resume_text = resume_text or read_resume_text(resume_file)

        if not question:
            question = interview_model.generate_question(
                role=role,
                difficulty=difficulty,
                category=category,
                resume_text=resume_text,
            )

        if not saved_video and not transcript:
            flash("Record or upload a video response before submitting to the AI interviewer.", "warning")
            return render_template(
                "practice.html",
                **practice_context,
                candidate_name=candidate_name,
                role=role,
                difficulty=difficulty,
                category=category,
                question=question,
                resume_text=resume_text,
            )

        practice_result = interview_model.review_answer(
            question=question,
            answer=transcript,
            candidate_name=candidate_name,
            role=role,
            difficulty=difficulty,
            category=category,
            video_filename=saved_video,
        )
        practice_result["analysis"]["recording_name"] = saved_video
        session_id = save_interview_session(
            practice_result["analysis"],
            user_id=current_user_id(),
            difficulty=difficulty,
            category=category,
            question=question,
        )
        practice_result["analysis"]["session_id"] = session_id
        return render_template("practice.html", result=practice_result, **practice_context)

    starter_question = interview_model.generate_question(
        role=PRACTICE_DEFAULTS["role"],
        difficulty=PRACTICE_DEFAULTS["difficulty"],
        category="HR",
    )
    mock_round = interview_model.generate_mock_round(
        role=PRACTICE_DEFAULTS["role"],
        difficulty=PRACTICE_DEFAULTS["difficulty"],
    )
    return render_template(
        "practice.html",
        **practice_context,
        candidate_name=PRACTICE_DEFAULTS["candidate_name"],
        role=PRACTICE_DEFAULTS["role"],
        difficulty=PRACTICE_DEFAULTS["difficulty"],
        category="HR",
        question=starter_question,
        mock_round=mock_round,
    )


@app.route("/practice/question")
def practice_question():
    role = request.args.get("role", "General Interview").strip() or "General Interview"
    difficulty = request.args.get("difficulty", "Beginner").strip() or "Beginner"
    category = request.args.get("category", "HR").strip() or "HR"
    return jsonify(
        {
            "question": interview_model.generate_question(role=role, difficulty=difficulty, category=category),
            "role": role,
            "difficulty": difficulty,
            "category": category,
        }
    )


@app.route("/history")
def history():
    sessions = list_interview_sessions(user_id=current_user_id())
    return render_template("history.html", sessions=sessions)


@app.route("/report/<int:session_id>")
def report(session_id):
    saved_session = get_interview_session(session_id, user_id=current_user_id())
    if not saved_session:
        flash("That saved interview report could not be found.", "warning")
        return redirect(url_for("history"))
    return render_template("report.html", saved_session=saved_session, analysis=saved_session["analysis"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = verify_user(email, password)
        if not user:
            flash("Email or password is incorrect.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["user"] = {"name": user["name"], "email": user["email"]}
        flash("Welcome back. Your interview history is ready.", "success")
        return redirect(url_for("history"))

    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip() or "Candidate"
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or len(password) < 6:
        flash("Use a valid email and a password with at least 6 characters.", "warning")
        return redirect(url_for("login"))

    try:
        user_id = create_user(name, email, password)
    except Exception:
        flash("That email already has an account. Please log in.", "warning")
        return redirect(url_for("login"))

    session["user_id"] = user_id
    session["user"] = {"name": name, "email": email.lower()}
    flash("Account created. New interview reports will be saved to your history.", "success")
    return redirect(url_for("practice"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


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
