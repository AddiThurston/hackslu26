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
const assignmentTitleInput = document.getElementById("assignmentTitle");
const assignmentTypeInput = document.getElementById("assignmentType");
const assignmentPointsInput = document.getElementById("assignmentPoints");
const assignmentStartInput = document.getElementById("assignmentStart");
const assignmentDueDateInput = document.getElementById("assignmentDueDate");
const reviewInfoPanel = document.getElementById("review-info-panel");
const noAssignmentDescriptionPanel = document.getElementById("no-assignment-description-panel");
const coursesSelect = document.getElementById("courses");
const canvasStatus = document.getElementById("canvasStatus");
const givePromptButton = document.getElementById("givePromptButton");
const assignmentPromptInput = document.getElementById("assignmentPromptInput");
const imagePreview = document.getElementById("image-preview");
const publishToggle = document.getElementById("publishToggle");
const assignmentsList = document.getElementById("assignments-list");
const apiKeyInput = document.getElementById("apiKeyInput");
const loginButton = document.getElementById("loginButton");
const logoutButton = document.getElementById("logoutButton");
const pdfInput = document.getElementById("pdfInput");
const previewTitle = document.getElementById("previewTitle");
const previewDescription = document.getElementById("previewDescription");
const previewDueDate = document.getElementById("previewDueDate");
const submissionTypeButtons = Array.from(
    document.querySelectorAll("[data-submission]")
);
let selectedSubmissionType = "online";
let generatedQuizQuestions = [];
let generatedQuizTitle = "";


const cachedApiKey = apiKeyInput ? localStorage.getItem("canvasApiKey") : null;

const setStep = (step) => {
    steps.forEach((item) => {
        item.classList.toggle("is-active", item.dataset.step === String(step));
    });
    panels.forEach((panel) => {
        panel.classList.toggle("is-hidden", panel.dataset.panel !== String(step));
    });
    if (step == 3) {
        previewTitle.textContent = assignmentTitleInput.value;
        previewDescription.textContent = assignmentDescriptionInput.value;
        previewDueDate.textContent = assignmentDueDateInput.value;
        console.log('test');
    }
};

const makeQuiz = async () => {
    if (!pdfInput || !pdfInput.files || !pdfInput.files[0]) {
        console.error("Missing lecture notes PDF.");
        return;
    }
    const formData = new FormData();
    formData.append("lectureNotes", pdfInput.files[0]);
    const response = await fetch("http://127.0.0.1:5000/makeQuiz", {
        method: "POST",
        body: formData,
    });
    const data = await response.json();
    const quizQuestionsContainer = document.getElementById("quizQuestions");
    const quizTitle = document.getElementById("quizTitle");
    if (!quizQuestionsContainer) {
        return;
    }
    if (quizTitle && pdfInput.files[0]) {
        const rawName = pdfInput.files[0].name || "Generated quiz";
        generatedQuizTitle = rawName.replace(/\.pdf$/i, "");
        quizTitle.textContent = generatedQuizTitle;
    }
    const rawParts = (data.quiz || "")
        .split("|")
        .map((part) => part.trim())
        .filter((part) => part.length > 0);
    if (rawParts.length % 4 !== 0) {
        console.debug("Quiz parse: unexpected part count", rawParts.length);
    }
    const questions = [];
    for (let i = 0; i < rawParts.length; i += 4) {
        questions.push({
            title: rawParts[i] || "Question",
            content: rawParts[i + 1] || "",
            type: rawParts[i + 2] || "essay_question",
            answers: rawParts[i + 3] || "",
        });
    }
    generatedQuizQuestions = questions;
    quizQuestionsContainer.innerHTML = questions
        .map((question, index) => {
            const answers = question.answers
                ? question.answers
                      .split(",")
                      .map((answer) => answer.trim())
                      .filter((answer) => answer.length > 0)
                : [];
            return `
            <div class="field-card">
                <div class="row row-between">
                    <h3>Question ${index + 1}: ${question.title}</h3>
                    <span class="mini-muted">${question.type}</span>
                </div>
                <p>${question.content}</p>
                ${
                    answers.length
                        ? `<div class="stack">
                            ${answers
                                .map(
                                    (answer) =>
                                        `<p class="mini-muted">Answer: ${answer}</p>`
                                )
                                .join("")}
                        </div>`
                        : ""
                }
            </div>
        `;
        })
        .join("");
    setStep(2);
};

const postQuiz = async () => {
    if (!coursesSelect || !coursesSelect.value) {
        console.error("Quiz post failed: no course selected");
        return;
    }
    if (!generatedQuizQuestions.length) {
        console.error("Quiz post failed: no generated questions");
        return;
    }
    try {
        const response = await fetch("http://127.0.0.1:5001/postQuiz", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                courseId: coursesSelect.value,
                quizTitle: generatedQuizTitle || "Generated quiz",
                questions: generatedQuizQuestions,
                publishImmediately: publishToggle ? publishToggle.checked : true,
            }),
        });
        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));
            console.error("Quiz post failed", errorBody);
        }
    } catch (error) {
        console.error("Quiz post failed", error);
    }
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

submissionTypeButtons.forEach((button) => {
    button.addEventListener("click", () => {
        submissionTypeButtons.forEach((item) =>
            item.classList.remove("is-active")
        );
        button.classList.add("is-active");
        selectedSubmissionType = button.dataset.submission || "online";
    });
});

if (assignmentDescriptionInput) {
    assignmentDescriptionInput.addEventListener("input", () => {
        if (assignmentDescriptionInput.value.trim() && noAssignmentDescriptionPanel) {
            noAssignmentDescriptionPanel.setAttribute("hidden", true);
        }
    });
}

function setloginstatus(isLoggedIn) {
    if (!canvasStatus) {
        return;
    }
    console.log(localStorage.getItem("canvasApiKey"));
    if (isLoggedIn) {
        if (window.location.pathname.includes('login.html')) {
        setCanvasStatus("status-good", "Logged in");
      } else {
        setCanvasStatus("status-warning", "Loading...");
      }
        
    } else {
        setCanvasStatus("status-warning", "Logged out");
    }
}

if (loginButton) {
    loginButton.addEventListener("click", async () => {
        if (!apiKeyInput || !apiKeyInput.value.trim()) {
            console.error("Missing Canvas API key.");
            return;
        }
        try {
            localStorage.setItem("canvasApiKey", apiKeyInput.value.trim());
            const response = await fetch("http://127.0.0.1:5001/setApiKey", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ apiKey: apiKeyInput.value.trim() }),
            });
            if (!response.ok) {
                const errorBody = await response.json().catch(() => ({}));
                console.error("Login failed", errorBody);
                setloginstatus(false);
                return;
            }
            setloginstatus(true);
        } catch (error) {
            console.error("Login failed", error);
            setloginstatus(false);
        }
    });
}

if (logoutButton) {
    logoutButton.addEventListener("click", async () => {
        try {
            localStorage.removeItem("canvasApiKey");
            const response = await fetch("http://127.0.0.1:5001/clearApiKey", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });
            if (!response.ok) {
                const errorBody = await response.json().catch(() => ({}));
                console.error("Logout failed", errorBody);
                loadCourses();
                return;
            }
            if (apiKeyInput) {
                apiKeyInput.value = "";
            }
            if (coursesSelect) {
                coursesSelect.innerHTML =
                    '<option value="">Login required</option>';
                coursesSelect.disabled = true;
            }
            setloginstatus(false);
        } catch (error) {
            console.error("Logout failed", error);
            loadCourses();
        }
    });
}

if (cachedApiKey && apiKeyInput) {
    apiKeyInput.value = cachedApiKey;
    fetch("http://127.0.0.1:5001/setApiKey", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ apiKey: cachedApiKey }),
    })
        .then((response) => {
            if (response.ok) {
                loadCourses();
            } else {
                setloginstatus(false);
            }
        })
        .catch((error) => {
            console.error("Auto-login failed", error);
            setloginstatus(false);
        });
} else {
    setloginstatus(false);
}

const showUploadFeedback = (name) => {
    const title = dropzone.querySelector("h2");
    if (title) {
        title.textContent = `Uploaded: ${name}`;
    }
};

function setCanvasStatus(state, message) {
    if (!canvasStatus) {
        return;
    }

    canvasStatus.textContent = message;
    canvasStatus.classList.remove("status-good", "status-warning", "status-fail");
    canvasStatus.classList.add(state);
}

const sendSelectedCourse = async () => {
    if (!coursesSelect || !coursesSelect.value) {
        return;
    }

    const selectedOption = coursesSelect.options[coursesSelect.selectedIndex];

    try {
        await fetch("http://127.0.0.1:5001/selected-course", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                courseId: coursesSelect.value,
                courseName: selectedOption ? selectedOption.textContent : "",
            }),
        });
    } catch (error) {
        console.error("Course selection sync failed", error);
    }
};

const loadCourses = async () => {
  if (window.location.pathname.includes('login.html')) {
    return;
  }
    if (!localStorage.getItem("canvasApiKey")) {
        if (coursesSelect) {
            coursesSelect.innerHTML = '<option value="">Login required</option>';
            coursesSelect.disabled = true;
        }
        setloginstatus(false);
        return;
    }
    setCanvasStatus("status-warning", "Loading...");
    if (!coursesSelect) {
        console.debug("canvasStatus->offline:loadCourses:no-select");
        setCanvasStatus("status-fail", "Offline");
        return;
    }

    coursesSelect.disabled = true;
    coursesSelect.innerHTML = '<option value="">Loading courses...</option>';

    try {
        const response = await fetch("http://127.0.0.1:5001/courses");
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            if (data && data.error === "Canvas API key not set.") {
                setloginstatus(false);
                coursesSelect.disabled = true;
                return;
            }
            if (response.status === 401) {
                setloginstatus(false);
                coursesSelect.innerHTML = '<option value="">Login required</option>';
                coursesSelect.disabled = true;
                return;
            }
            console.error("Course load failed", data);
            console.debug("canvasStatus->offline:loadCourses:response-not-ok");
            setCanvasStatus("status-fail", "Offline");
            throw new Error(`Course request failed: ${response.status}`);
        }
        const courses = Array.isArray(data.courses) ? data.courses : [];

        if (courses.length === 0) {
            coursesSelect.innerHTML =
                '<option value="">No teacher courses found</option>';
            return;
        }

        coursesSelect.innerHTML = courses
            .map((course) => `<option value="${course.id}">${course.name}</option>`)
            .join("");
        setCanvasStatus("status-good", "Connected");
        if (window.location.pathname.includes('assignments.html')) {
            getAssignments();
        }
        await sendSelectedCourse();
    } catch (error) {
        console.error("Course load failed", error);
        coursesSelect.innerHTML =
            '<option value="">Unable to load courses</option>';
        console.debug("canvasStatus->offline:loadCourses:catch");
        setCanvasStatus("status-fail", "Offline");
    } finally {
        coursesSelect.disabled = false;
    }
};

const uploadToVision = async (file) => {
    const formData = new FormData();
    formData.append("image", file);
    const endpoint = "http://127.0.0.1:5000/scan";
    if (noAssignmentDescriptionPanel) {
        noAssignmentDescriptionPanel.setAttribute("hidden", true);
    }

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Vision request failed: ${response.status}`);
        }

        const data = await response.json();
        // fill the fields with the data from the vision api
        if (assignmentDescriptionInput && data.text) {
            const fields = data.text.split("|");
            assignmentTitleInput.value = fields[1];
            assignmentTypeInput.value = fields[2];
            assignmentDescriptionInput.value = fields[3];
            assignmentPointsInput.value = fields[4];
            assignmentStartInput.value = fields[5];
            assignmentDueDateInput.value = fields[6];
            reviewInfoPanel.removeAttribute("hidden");
            noAssignmentDescriptionPanel.setAttribute("hidden", true);

            previewDueDate.textContent = "Due: " + fields[6] + " at 11:59 PM";
            previewDescription.textContent = fields[3];
            previewTitle.textContent = fields[1];
        }
    } catch (error) {
        console.error("Vision upload failed", error);
    }
};

const givePrompt = async () => {
    if (!assignmentPromptInput.value) {
        return;
    }
    if (noAssignmentDescriptionPanel) {
        noAssignmentDescriptionPanel.setAttribute("hidden", true);
    }
    try {
        const response = await fetch("http://127.0.0.1:5000/givePrompt", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                assignmentPrompt: assignmentPromptInput.value,
            }),
        });
        const data = await response.json();
        if (assignmentPromptInput && data.text) {
          const fields = data.text.split("|");
          assignmentTitleInput.value = fields[1];
          assignmentTypeInput.value = fields[2];
          assignmentDescriptionInput.value = fields[3];
          assignmentPointsInput.value = fields[4];
          assignmentStartInput.value = fields[5];
          assignmentDueDateInput.value = fields[6];
          reviewInfoPanel.removeAttribute("hidden");
          noAssignmentDescriptionPanel.setAttribute("hidden", true);

          previewDueDate.textContent = "Due: " + fields[6] + " at 11:59 PM";
          previewDescription.textContent = fields[3];
          previewTitle.textContent = fields[1];
          imagePreview.setAttribute("hidden", true);
        }
    } catch (error) {
        console.error("Assignment prompt failed", error);
    }
};

const postAssignment = async () => {
    if (!coursesSelect || !coursesSelect.value) {
        console.error("Assignment post failed: no course selected");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5001/postAssignment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                courseId: coursesSelect.value,
                courseName:
                    coursesSelect.options[coursesSelect.selectedIndex]?.textContent ||
                    "",
                assignmentNameInput: assignmentTitleInput.value,
                assignmentDescriptionInput: assignmentDescriptionInput.value,
                assignmentPointsInput: assignmentPointsInput.value,
                assignmentStartInput: assignmentStartInput.value,
                assignmentDueDateInput: assignmentDueDateInput.value,
                submissionType: selectedSubmissionType,
                publishImmediately: publishToggle ? publishToggle.checked : true,
            }),
        });

        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));
            console.error("Assignment post failed", errorBody);
        }
    } catch (error) {
        console.error("Assignment post failed", error);
    }
};

const getAssignments = async () => {
    if (!coursesSelect || !coursesSelect.value) {
        console.error("Assignment get failed: no course selected");
        return;
    }
    try {
        const response = await fetch(
            `http://127.0.0.1:5001/getAssignments?courseId=${encodeURIComponent(
                coursesSelect.value
            )}`,
            {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            }
        );
        const data = await response.json();
        const assignments = Array.isArray(data.assignments) ? data.assignments : [];
        console.log(assignments);

        assignmentsList.innerHTML = assignments.map((assignment) => 
          `<li class="assignment-card">
            <h3>${assignment.name}</h3>
            <p>${assignment.points_possible} points</p>
            <p>Due: ${assignment.due_at ? new Date(assignment.due_at).toLocaleDateString() : "N/A"}</p>
            <button class="button2 ${assignment.published == true ? "status-good" : "status-fail"}" onclick="togglePublish(${assignment.id}, ${assignment.published})">
              ${assignment.published ? "Published" : "Unpublished"}
            </button>

            <button class="button2 status-fail" onclick="deleteAssignment(${assignment.id}, ${coursesSelect.value})">
              Delete
            </button>
          </li>`).join("");
        return assignments;
    } catch (error) {
        console.error("Assignment get failed", error);
        return [];
    }
};

const togglePublish = async (assignmentId, published) => {
    try {
        const nextPublished = !published;
        const response = await fetch(`http://127.0.0.1:5001/togglePublish`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                assignmentId: assignmentId,
                courseId: coursesSelect ? coursesSelect.value : null,
                published: nextPublished,
            }),
        });
        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));
            console.error("Toggle publish failed", errorBody);
            return;
        }
        getAssignments();
    }
    catch (error) {
        console.error("Toggle publish failed", error);
    }
};

const deleteAssignment = async (assignmentId, courseId) => {
  try {
      const response = await fetch(`http://127.0.0.1:5001/deleteAssignment`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ assignmentId: assignmentId, courseId: courseId }),
      });
      getAssignments();
  }
  catch (error) {
      console.error("Delete assignment failed", error);
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

if (pdfInput) {
  pdfInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) {
      makeQuiz(file);
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
            uploadToVision(file);
        }
    });
}

if (canvasStatus) {
    canvasStatus.addEventListener("click", () => {
        loadCourses();
        setloginstatus(localStorage.getItem("canvasApiKey") != null);
    });
}

if (coursesSelect) {
    coursesSelect.addEventListener("change", () => {
        sendSelectedCourse();
        if (window.location.pathname.includes('assignments.html')) {
            getAssignments();
        }
    });
    loadCourses();
}

if (postButton) {
    postButton.addEventListener("click", () => {
        if (postProgress) {
            postProgress.style.display = "flex";
        }
        if (successCard) {
            successCard.style.display = "none";
        }
        postButton.disabled = true;

        setTimeout(() => {
            if (postProgress) {
                postProgress.style.display = "none";
            }
            if (successCard) {
                successCard.style.display = "block";
            }
            postButton.disabled = false;
        }, 1600);
        if (window.location.pathname.includes("quiz.html")) {
            postQuiz();
        } else {
            postAssignment();
        }
    });
}

if (givePromptButton) {
  givePromptButton.addEventListener("click", () => {
      setStep(2);
      givePrompt();
  });
}

setloginstatus(localStorage.getItem("canvasApiKey") != null);