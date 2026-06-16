const form = document.getElementById("videoPracticeForm");
const cameraPreview = document.getElementById("cameraPreview");
const recordedPreview = document.getElementById("recordedPreview");
const videoInput = document.getElementById("video_response");
const startCameraButton = document.getElementById("startCameraButton");
const startRecordingButton = document.getElementById("startRecordingButton");
const stopRecordingButton = document.getElementById("stopRecordingButton");

let mediaStream = null;
let mediaRecorder = null;
let recordedChunks = [];

async function startCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Camera recording is not supported in this browser. Upload a video file instead.");
    return;
  }

  mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  cameraPreview.srcObject = mediaStream;
  startRecordingButton.disabled = false;
}

function startRecording() {
  if (!mediaStream) return;

  recordedChunks = [];
  mediaRecorder = new MediaRecorder(mediaStream, { mimeType: "video/webm" });
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
  };

  mediaRecorder.start();
  startRecordingButton.disabled = true;
  stopRecordingButton.disabled = false;
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  }

  stopRecordingButton.disabled = true;
  startRecordingButton.disabled = false;
}

startCameraButton?.addEventListener("click", () => {
  startCamera().catch(() => {
    alert("Camera permission was not granted. Upload a video file instead.");
  });
});

startRecordingButton?.addEventListener("click", startRecording);
stopRecordingButton?.addEventListener("click", stopRecording);

form?.addEventListener("submit", () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
  }
});
