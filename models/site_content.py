HOME_CONTENT = {
    "eyebrow": "AI interview lab",
    "title": "Practice live interviews with video, voice, and instant scoring.",
    "summary": (
        "A student can answer on camera, submit interview notes or recordings, "
        "and receive Python-generated feedback on confidence, clarity, pace, fillers, and response quality."
    ),
    "chips": [
        "Live Video Practice",
        "AI Voice Questions",
        "Resume Questions",
        "Saved History",
        "PDF Reports",
        "Python Scoring",
    ],
    "stats": [
        {"value": "10", "label": "Portfolio features"},
        {"value": "5", "label": "Question categories"},
        {"value": "50MB", "label": "Recording uploads"},
    ],
}

DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

PRACTICE_DEFAULTS = {
    "candidate_name": "Harshita Gautam",
    "role": "Python Developer",
    "difficulty": "Beginner",
}

SAMPLE_TRANSCRIPTS = {
    "project": (
        "I built a student attendance dashboard in Python using Flask and simple charts. "
        "I handled the form flow, cleaned the data, and improved the report page so teachers "
        "could understand daily attendance faster. The result was a clearer workflow and fewer manual checks."
    ),
    "teamwork": (
        "In a team project, I managed the backend tasks and coordinated with the frontend member. "
        "When we found a bug near submission time, I explained the issue clearly, fixed the route, "
        "and helped deliver the project on time with a working demo."
    ),
    "learning": (
        "I learn best by building small projects. When I struggled with Flask routing, I created practice pages, "
        "tested each route, and documented what worked. That helped me become more confident with Python web development."
    ),
}


def get_sample_transcript(sample_key):
    return SAMPLE_TRANSCRIPTS.get(sample_key, SAMPLE_TRANSCRIPTS["project"])
