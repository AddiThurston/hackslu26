const steps = Array.from(document.querySelectorAll(".step"));
const panels = Array.from(document.querySelectorAll(".step-panel"));
const fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const postButton = document.getElementById("postButton");
const postProgress = document.getElementById("postProgress");
const successCard = document.getElementById("successCard");

const setStep = (step) => {
  steps.forEach((item) => {
    item.classList.toggle("is-active", item.dataset.step === String(step));
  });
  panels.forEach((panel) => {
    panel.classList.toggle("is-hidden", panel.dataset.panel !== String(step));
  });
};

document.querySelectorAll("[data-next]").forEach((button) => {
  button.addEventListener("click", () => {
    const next = button.dataset.next;
    setStep(next);
  });
});

document.querySelectorAll("[data-back]").forEach((button) => {
  button.addEventListener("click", () => {
    const back = button.dataset.back;
    setStep(back);
  });
});

steps.forEach((step) => {
  step.addEventListener("click", () => setStep(step.dataset.step));
});

const showUploadFeedback = (name) => {
  const title = dropzone.querySelector("h2");
  if (title) {
    title.textContent = `Uploaded: ${name}`;
  }
};

if (fileInput) {
  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) {
      showUploadFeedback(file.name);
      setStep(2);
    }
  });
}

if (dropzone) {
  dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("is-dragover");
  });

  dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragover");
    const file = event.dataTransfer.files[0];
    if (file) {
      showUploadFeedback(file.name);
      setStep(2);
    }
  });
}

if (postButton) {
  postButton.addEventListener("click", () => {
    postProgress.style.display = "flex";
    successCard.style.display = "none";
    postButton.disabled = true;

    setTimeout(() => {
      postProgress.style.display = "none";
      successCard.style.display = "block";
      postButton.disabled = false;
    }, 1600);
  });
}
