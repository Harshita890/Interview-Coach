const transcriptField = document.getElementById("transcript");
const transcriptCount = document.getElementById("transcriptCount");
const sampleButtons = document.querySelectorAll(".sample-answer-button");

function countWords(text) {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

function updateTranscriptCount() {
  if (!transcriptField || !transcriptCount) return;
  const words = countWords(transcriptField.value);
  transcriptCount.textContent = `${words} ${words === 1 ? "word" : "words"}`;
}

async function loadSampleAnswer(sampleKey) {
  const response = await fetch(`/sample-answer/${sampleKey}`);
  if (!response.ok) {
    throw new Error("Sample answer could not be loaded.");
  }

  const data = await response.json();
  transcriptField.value = data.transcript;
  updateTranscriptCount();
  transcriptField.focus();
}

transcriptField?.addEventListener("input", updateTranscriptCount);

sampleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    loadSampleAnswer(button.dataset.sample).catch(() => {
      alert("Could not load that sample answer. Please type your own transcript.");
    });
  });
});

updateTranscriptCount();
