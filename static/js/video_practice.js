const form = document.getElementById("videoPracticeForm");
const roleInput = document.getElementById("role");
const difficultyInput = document.getElementById("difficulty");
const questionInput = document.getElementById("question");
const transcriptInput = document.getElementById("transcript");
const cameraPreview = document.getElementById("cameraPreview");
const recordedPreview = document.getElementById("recordedPreview");
const videoInput = document.getElementById("video_response");
const startCameraButton = document.getElementById("startCameraButton");
const startRecordingButton = document.getElementById("startRecordingButton");
const stopRecordingButton = document.getElementById("stopRecordingButton");
const startInterviewButton = document.getElementById("startInterviewButton");
const askQuestionButton = document.getElementById("askQuestionButton");
const newQuestionButton = document.getElementById("newQuestionButton");
const submitPracticeButton = document.getElementById("submitPracticeButton");
const statusText = document.getElementById("statusText");
const speechSupportText = document.getElementById("speechSupportText");
const recordingPill = document.getElementById("recordingPill");
const recordingTimer = document.getElementById("recordingTimer");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let recognition = null;
let finalTranscript = "";
let timerId = null;
let recordingStartedAt = null;
let pendingSubmitAfterStop = false;

function setStatus(message) {
  if (statusText) {
    statusText.textContent = message;
  }
}

function setButtonsForRecording(isRecording) {
  startRecordingButton.disabled = isRecording || !mediaStream;
  stopRecordingButton.disabled = !isRecording;
  startInterviewButton.disabled = isRecording;
  submitPracticeButton.disabled = isRecording;
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

async function startCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Camera recording is not supported in this browser. Upload a video file instead.");
    return false;
  }

  if (mediaStream) {
    return true;
  }

  mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  cameraPreview.srcObject = mediaStream;
  startRecordingButton.disabled = false;
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
    speechSupportText.textContent = "Live speech capture stopped. You can continue typing notes.";
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
    if (event.data.size > 0) {
      recordedChunks.push(event.data);
    }
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
    setButtonsForRecording(false);
    setStatus("Response recorded");

    if (pendingSubmitAfterStop) {
      pendingSubmitAfterStop = false;
      HTMLFormElement.prototype.submit.call(form);
    }
  };

  mediaRecorder.start();
  startTimer();
  startSpeechCapture();
  setButtonsForRecording(true);
  setStatus("Recording answer");
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }
}

function speakQuestion({ onEnd } = {}) {
  const question = questionInput.value.trim();
  if (!question) return;

  if (!window.speechSynthesis) {
    setStatus("Question ready");
    if (onEnd) onEnd();
    return;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(question);
  utterance.rate = 0.95;
  utterance.pitch = 1;
  utterance.onstart = () => setStatus("AI asking question");
  utterance.onend = () => {
    setStatus("Answer now");
    if (onEnd) onEnd();
  };
  window.speechSynthesis.speak(utterance);
}

async function loadNewQuestion() {
  const params = new URLSearchParams({
    role: roleInput.value || "General Interview",
    difficulty: difficultyInput.value || "Beginner",
  });

  setStatus("Loading question");
  const response = await fetch(`/practice/question?${params.toString()}`);
  if (!response.ok) {
    throw new Error("Could not load a new question.");
  }

  const data = await response.json();
  questionInput.value = data.question;
  setStatus("Question ready");
  return data.question;
}

async function startLiveInterview() {
  const cameraReady = await startCamera();
  if (!cameraReady) return;

  recordedPreview.classList.add("d-none");
  transcriptInput.value = "";
  finalTranscript = "";
  videoInput.value = "";
  speakQuestion({ onEnd: startRecording });
}

startCameraButton?.addEventListener("click", () => {
  startCamera().catch(() => {
    alert("Camera permission was not granted. Upload a video file instead.");
    setStatus("Camera blocked");
  });
});

startRecordingButton?.addEventListener("click", startRecording);
stopRecordingButton?.addEventListener("click", stopRecording);
askQuestionButton?.addEventListener("click", () => speakQuestion());
startInterviewButton?.addEventListener("click", () => {
  startLiveInterview().catch(() => {
    alert("Camera or microphone permission was not granted. Upload a video file instead.");
    setStatus("Permission needed");
  });
});
newQuestionButton?.addEventListener("click", () => {
  loadNewQuestion().catch(() => {
    alert("The app could not load a new question. You can edit the question manually.");
    setStatus("Question unchanged");
  });
});

form?.addEventListener("submit", (event) => {
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
