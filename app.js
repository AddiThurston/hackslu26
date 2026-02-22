const steps = Array.from(document.querySelectorAll(".step")); // store all the steps
const panels = Array.from(document.querySelectorAll(".step-panel")); // store all the step panels
const fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const postButton = document.getElementById("postButton");
const retakeButton = document.getElementById("retake-button");
const uploadedImage = document.getElementById("uploadedImage");
const postProgress = document.getElementById("postProgress");
const successCard = document.getElementById("successCard");
const assignmentDescriptionInput = document.getElementById("assignmentDescription");
const courseNameInput = document.getElementById("courseName");
const assignmentTitleInput = document.getElementById("assignmentTitle");
const assignmentTypeInput = document.getElementById("assignmentType");
const assignmentPointsInput = document.getElementById("assignmentPoints");
const assignmentStartInput = document.getElementById("assignmentStart");
const assignmentDueDateInput = document.getElementById("assignmentDueDate");

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

const uploadToVision = async (file) => {
  const formData = new FormData();
  formData.append("image", file);
  const endpoint = "http://127.0.0.1:5000/scan";

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Vision request failed: ${response.status}`);
    }

    const data = await response.json();
    if (assignmentDescriptionInput && data.text) {
      const fields = data.text.split("|");
      courseNameInput.value = fields[0];
      assignmentTitleInput.value = fields[1];
      assignmentTypeInput.value = fields[2];
      assignmentDescriptionInput.value = fields[3];
      assignmentPointsInput.value = fields[4];
      assignmentStartInput.value = fields[5];
      assignmentDueDateInput.value = fields[6];
      console.log(fields);
    }
  } catch (error) {
    console.error("Vision upload failed", error);
  }
};

if (fileInput) {
  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) {
      uploadedImage.src = URL.createObjectURL(file);
      uploadedImage.removeAttribute("hidden");
      retakeButton.removeAttribute("hidden");
      showUploadFeedback(file.name);
      setStep(2);
      uploadToVision(file);
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
      uploadToVision(file);
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
