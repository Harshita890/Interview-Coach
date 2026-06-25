const form = document.getElementById("videoPracticeForm");
const candidateInput = document.getElementById("candidate_name");
const roleInput = document.getElementById("role");
const difficultyInput = document.getElementById("difficulty");
const categoryInput = document.getElementById("category");
const resumeTextInput = document.getElementById("resume_text");
const questionInput = document.getElementById("question");
const allQuestionsInput = document.getElementById("all_questions");
const transcriptInput = document.getElementById("transcript");
const cameraPreview = document.getElementById("cameraPreview");
const recordedPreview = document.getElementById("recordedPreview");
const videoInput = document.getElementById("video_response");
const startInterviewButton = document.getElementById("startInterviewButton");
const nextQuestionButton = document.getElementById("nextQuestionButton");
const repeatQuestionButton = document.getElementById("repeatQuestionButton");
const stopRecordingButton = document.getElementById("stopRecordingButton");
const submitPracticeButton = document.getElementById("submitPracticeButton");
const exitRoomButton = document.getElementById("exitRoomButton");
const statusText = document.getElementById("statusText");
const speechSupportText = document.getElementById("speechSupportText");
const recordingPill = document.getElementById("recordingPill");
const recordingTimer = document.getElementById("recordingTimer");
const interviewRoom = document.getElementById("interviewRoom");
const roomProgressText = document.getElementById("roomProgressText");
const roomCandidateLabel = document.getElementById("roomCandidateLabel");
const roomRoundLabel = document.getElementById("roomRoundLabel");
const liveQuestionText = document.getElementById("liveQuestionText");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let recognition = null;
let finalTranscript = "";
let timerId = null;
let recordingStartedAt = null;
let pendingSubmitAfterStop = false;
let roundQuestions = [];
let currentQuestionIndex = 0;
let currentSpokenPrompt = "";

function setStatus(message) {
  if (statusText) statusText.textContent = message;
}

function formatTimer(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function startTimer() {
  recordingStartedAt = Date.now();
  recordingPill.classList.remove("d-none");
  recordingTimer.textContent = "00:00";
  timerId = window.setInterval(() => {
    const elapsed = Math.floor((Date.now() - recordingStartedAt) / 1000);
    recordingTimer.textContent = formatTimer(elapsed);
  }, 1000);
}

function stopTimer() {
  window.clearInterval(timerId);
  timerId = null;
  recordingPill.classList.add("d-none");
}

function validateSetup() {
  if (!candidateInput.value.trim()) {
    candidateInput.focus();
    alert("Please enter the candidate name.");
    return false;
  }
  if (!roleInput.value.trim()) {
    roleInput.focus();
    alert("Please enter the target role.");
    return false;
  }
  return true;
}

async function startCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Camera recording is not supported in this browser. Upload a video file instead.");
    return false;
  }

  if (mediaStream) return true;

  mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  cameraPreview.srcObject = mediaStream;
  stopRecordingButton.disabled = false;
  setStatus("Camera ready");
  return true;
}

function createMediaRecorder() {
  const preferredTypes = [
    "video/webm;codecs=vp9,opus",
    "video/webm;codecs=vp8,opus",
    "video/webm",
  ];
  const supportedType = preferredTypes.find((type) => MediaRecorder.isTypeSupported(type));
  return supportedType ? new MediaRecorder(mediaStream, { mimeType: supportedType }) : new MediaRecorder(mediaStream);
}

function setupSpeechRecognition() {
  if (!SpeechRecognition) {
    speechSupportText.textContent = "Live speech capture is not supported here. Type notes while answering.";
    return null;
  }

  const speechRecognition = new SpeechRecognition();
  speechRecognition.continuous = true;
  speechRecognition.interimResults = true;
  speechRecognition.lang = "en-US";
  speechRecognition.onstart = () => {
    speechSupportText.textContent = "Listening and writing answer notes live.";
  };
  speechRecognition.onresult = (event) => {
    let interimTranscript = "";
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      const transcript = event.results[index][0].transcript;
      if (event.results[index].isFinal) {
        finalTranscript = `${finalTranscript} ${transcript}`.trim();
      } else {
        interimTranscript = `${interimTranscript} ${transcript}`.trim();
      }
    }
    transcriptInput.value = [finalTranscript, interimTranscript].filter(Boolean).join(" ");
  };
  speechRecognition.onerror = () => {
    speechSupportText.textContent = "Live speech capture paused. You can continue typing notes.";
  };
  speechRecognition.onend = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      try {
        speechRecognition.start();
      } catch (error) {
        speechSupportText.textContent = "Live speech capture paused. You can continue typing notes.";
      }
    }
  };

  return speechRecognition;
}

function startSpeechCapture() {
  recognition = setupSpeechRecognition();
  finalTranscript = transcriptInput.value.trim();

  if (recognition) {
    try {
      recognition.start();
    } catch (error) {
      speechSupportText.textContent = "Live speech capture is already active.";
    }
  }
}

function stopSpeechCapture() {
  if (recognition) {
    recognition.onend = null;
    recognition.stop();
    recognition = null;
  }
  speechSupportText.textContent = "Answer notes are ready to review before submitting.";
}

function startRecording() {
  if (!mediaStream) return;

  recordedChunks = [];
  mediaRecorder = createMediaRecorder();
  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) recordedChunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, { type: "video/webm" });
    const file = new File([blob], "ai-interview-response.webm", { type: "video/webm" });
    const transfer = new DataTransfer();
    transfer.items.add(file);
    videoInput.files = transfer.files;

    recordedPreview.src = URL.createObjectURL(blob);
    recordedPreview.classList.remove("d-none");
    stopTimer();
    stopSpeechCapture();
    stopRecordingButton.disabled = true;
    setStatus("Response recorded");

    if (pendingSubmitAfterStop) {
      pendingSubmitAfterStop = false;
      HTMLFormElement.prototype.submit.call(form);
    }
  };

  mediaRecorder.start();
  startTimer();
  startSpeechCapture();
  setStatus("Interview recording");
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
}

function speak(text, { onEnd } = {}) {
  currentSpokenPrompt = text;

  if (!window.speechSynthesis) {
    setStatus("AI voice unavailable");
    if (onEnd) onEnd();
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;
  utterance.pitch = 1;
  utterance.onstart = () => setStatus("AI speaking");
  utterance.onend = () => {
    setStatus("Answer now");
    if (onEnd) onEnd();
  };
  window.speechSynthesis.speak(utterance);
}

function updateRoomProgress() {
  const total = roundQuestions.length || 7;
  const number = Math.min(currentQuestionIndex + 1, total);
  roomProgressText.textContent = `Question ${number} of ${total}`;
  liveQuestionText.textContent = "Listen to the AI voice, then answer on camera.";
}

function appendQuestionMarker(question) {
  const marker = `\n\nAnswer ${currentQuestionIndex + 1}:`;
  transcriptInput.value = `${transcriptInput.value.trim()}${marker}`;
  finalTranscript = transcriptInput.value;
}

function askCurrentQuestion() {
  if (!roundQuestions[currentQuestionIndex]) return;
  const question = roundQuestions[currentQuestionIndex];
  questionInput.value = question;
  updateRoomProgress();
  appendQuestionMarker(question);
  speak(question);
}

async function loadInterviewRound() {
  const response = await fetch("/practice/round", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_name: candidateInput.value,
      role: roleInput.value,
      difficulty: difficultyInput.value,
      category: categoryInput.value,
      resume_text: resumeTextInput.value,
    }),
  });

  if (!response.ok) throw new Error("Could not create interview round.");
  const data = await response.json();
  roundQuestions = data.questions || [];
  allQuestionsInput.value = roundQuestions.map((question, index) => `${index + 1}. ${question}`).join("\n");
  return data;
}

async function startLiveInterview() {
  if (!validateSetup()) return;

  const cameraReady = await startCamera();
  if (!cameraReady) return;

  const data = await loadInterviewRound();
  currentQuestionIndex = 0;
  transcriptInput.value = "";
  finalTranscript = "";
  videoInput.value = "";
  recordedPreview.classList.add("d-none");

  roomCandidateLabel.textContent = `${candidateInput.value.trim()} - ${roleInput.value.trim()}`;
  roomRoundLabel.textContent = `${categoryInput.value} round`;
  interviewRoom.classList.remove("d-none");
  document.body.classList.add("room-open");

  startRecording();
  speak(data.greeting, { onEnd: askCurrentQuestion });
}

function moveToNextQuestion() {
  if (currentQuestionIndex >= roundQuestions.length - 1) {
    speak("That was the final question. Please finish your answer, then submit the interview for review.");
    roomProgressText.textContent = "Final answer";
    nextQuestionButton.disabled = true;
    return;
  }

  currentQuestionIndex += 1;
  askCurrentQuestion();
}

function exitRoom() {
  window.speechSynthesis?.cancel();
  interviewRoom.classList.add("d-none");
  document.body.classList.remove("room-open");
}

startInterviewButton?.addEventListener("click", () => {
  startLiveInterview().catch(() => {
    alert("Camera, microphone, or AI round setup failed. Please check permission and try again.");
    setStatus("Permission needed");
  });
});

nextQuestionButton?.addEventListener("click", moveToNextQuestion);
repeatQuestionButton?.addEventListener("click", () => speak(currentSpokenPrompt || questionInput.value));
stopRecordingButton?.addEventListener("click", stopRecording);
exitRoomButton?.addEventListener("click", exitRoom);

form?.addEventListener("submit", (event) => {
  window.speechSynthesis?.cancel();

  if (mediaRecorder && mediaRecorder.state === "recording") {
    event.preventDefault();
    pendingSubmitAfterStop = true;
    setStatus("Saving response");
    mediaRecorder.stop();
    return;
  }

  stopSpeechCapture();
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
  }
});
