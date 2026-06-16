import re
from collections import Counter


FILLER_PATTERNS = {
    "um": r"\b(?:um+|umm+|uhm+)\b",
    "uh": r"\b(?:uh+|uhh+)\b",
    "like": r"\blike\b",
    "you know": r"\byou know\b",
    "actually": r"\bactually\b",
    "basically": r"\bbasically\b",
}

POSITIVE_WORDS = {
    "achieved",
    "adaptable",
    "built",
    "clear",
    "collaborated",
    "confident",
    "delivered",
    "effective",
    "excited",
    "improved",
    "led",
    "learned",
    "positive",
    "resolved",
    "successful",
    "strong",
}

NEGATIVE_WORDS = {
    "afraid",
    "bad",
    "confused",
    "difficult",
    "failed",
    "hard",
    "nervous",
    "problem",
    "struggle",
    "unsure",
    "weak",
    "worried",
}

CONFIDENCE_WORDS = {
    "i led",
    "i built",
    "i created",
    "i improved",
    "i solved",
    "i managed",
    "i delivered",
    "i learned",
}

HESITATION_WORDS = {
    "maybe",
    "probably",
    "kind of",
    "sort of",
    "i guess",
    "i think",
    "not sure",
}


def analyze_interview(transcript, candidate_name, role, duration_minutes=None, recording_name=None):
    text = transcript.strip()
    if not text:
        text = (
            "Audio uploaded successfully. Add speech-to-text integration such as Whisper "
            "to generate a full transcript from this recording."
        )

    words = _words(text)
    word_count = len(words)
    sentence_count = max(len(re.findall(r"[.!?]+", text)), 1)
    estimated_duration = duration_minutes or max(word_count / 135, 1)
    speaking_pace = round(word_count / estimated_duration)
    filler_counts = _count_fillers(text)
    total_fillers = sum(filler_counts.values())
    sentiment = _sentiment(words)
    confidence_score = _confidence_score(text, word_count, total_fillers)
    communication_score = _communication_score(word_count, sentence_count, speaking_pace, total_fillers)
    response_quality = _response_quality_score(text, word_count)
    overall_score = round(
        (confidence_score * 0.3)
        + (communication_score * 0.3)
        + (sentiment["score"] * 0.2)
        + (response_quality * 0.2)
    )

    return {
        "candidate_name": candidate_name,
        "role": role,
        "recording_name": recording_name,
        "transcript": text,
        "metrics": {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "duration_minutes": round(estimated_duration, 2),
            "speaking_pace": speaking_pace,
            "total_fillers": total_fillers,
            "filler_counts": filler_counts,
            "confidence_score": confidence_score,
            "communication_score": communication_score,
            "response_quality": response_quality,
            "overall_score": overall_score,
        },
        "sentiment": sentiment,
        "strengths": _strengths(confidence_score, communication_score, sentiment, response_quality),
        "improvements": _improvements(speaking_pace, total_fillers, confidence_score, response_quality),
        "recommendations": _recommendations(speaking_pace, total_fillers, confidence_score, response_quality),
    }


def _words(text):
    return re.findall(r"[A-Za-z']+", text.lower())


def _count_fillers(text):
    lowered = text.lower()
    return {
        label: len(re.findall(pattern, lowered))
        for label, pattern in FILLER_PATTERNS.items()
        if len(re.findall(pattern, lowered)) > 0
    }


def _sentiment(words):
    counts = Counter(words)
    positive = sum(counts[word] for word in POSITIVE_WORDS)
    negative = sum(counts[word] for word in NEGATIVE_WORDS)
    raw = positive - negative

    if raw > 1:
        label = "Positive"
        score = min(95, 70 + raw * 5)
    elif raw < -1:
        label = "Negative"
        score = max(35, 60 + raw * 5)
    else:
        label = "Neutral"
        score = 68

    return {
        "label": label,
        "score": score,
        "positive_terms": positive,
        "negative_terms": negative,
    }


def _confidence_score(text, word_count, total_fillers):
    lowered = text.lower()
    confident_phrases = sum(lowered.count(phrase) for phrase in CONFIDENCE_WORDS)
    hesitation_phrases = sum(lowered.count(phrase) for phrase in HESITATION_WORDS)
    length_bonus = min(12, word_count // 25)
    filler_penalty = min(20, total_fillers * 3)
    hesitation_penalty = min(18, hesitation_phrases * 4)
    score = 62 + confident_phrases * 5 + length_bonus - filler_penalty - hesitation_penalty
    return _clamp(score)


def _communication_score(word_count, sentence_count, speaking_pace, total_fillers):
    average_sentence_length = word_count / sentence_count
    pace_score = 100 - min(abs(speaking_pace - 135), 80)
    sentence_score = 100 - min(abs(average_sentence_length - 18) * 3, 60)
    filler_penalty = min(25, total_fillers * 3)
    return _clamp((pace_score * 0.55) + (sentence_score * 0.45) - filler_penalty)


def _response_quality_score(text, word_count):
    lowered = text.lower()
    structure_terms = ["situation", "task", "action", "result", "because", "therefore", "example"]
    structure_hits = sum(1 for term in structure_terms if term in lowered)
    length_score = min(85, word_count * 1.4)
    score = 45 + structure_hits * 7 + length_score * 0.35
    return _clamp(score)


def _strengths(confidence_score, communication_score, sentiment, response_quality):
    strengths = []
    if confidence_score >= 70:
        strengths.append("Shows confident ownership of experience and decisions.")
    if communication_score >= 70:
        strengths.append("Maintains a clear speaking rhythm and understandable structure.")
    if sentiment["label"] == "Positive":
        strengths.append("Uses positive language that creates an engaged impression.")
    if response_quality >= 70:
        strengths.append("Provides enough detail for the interviewer to evaluate the answer.")
    return strengths or ["The response gives a starting point for focused interview practice."]


def _improvements(speaking_pace, total_fillers, confidence_score, response_quality):
    improvements = []
    if speaking_pace < 110:
        improvements.append("Increase speaking energy slightly to avoid sounding hesitant.")
    elif speaking_pace > 165:
        improvements.append("Slow down and add short pauses between key points.")
    if total_fillers > 3:
        improvements.append("Reduce filler words by pausing silently before continuing.")
    if confidence_score < 70:
        improvements.append("Use more direct, ownership-focused phrases when describing work.")
    if response_quality < 70:
        improvements.append("Add a concrete example with action taken and measurable result.")
    return improvements or ["Keep practicing consistency across different interview questions."]


def _recommendations(speaking_pace, total_fillers, confidence_score, response_quality):
    recommendations = [
        "Practice answers using the STAR method: situation, task, action, and result.",
        "Record a second attempt and compare filler count, pace, and confidence score.",
    ]
    if total_fillers > 0:
        recommendations.append("Replace filler words with one-second pauses.")
    if speaking_pace > 165 or speaking_pace < 110:
        recommendations.append("Aim for a speaking pace between 120 and 150 words per minute.")
    if confidence_score < 75:
        recommendations.append("Start key answers with a clear claim, then support it with evidence.")
    if response_quality < 75:
        recommendations.append("Include numbers, tools, outcomes, or lessons learned in each answer.")
    return recommendations


def _clamp(value, minimum=0, maximum=100):
    return int(max(minimum, min(maximum, round(value))))
