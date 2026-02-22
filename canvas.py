import os
from datetime import datetime, time, timezone
from flask import Flask, jsonify, make_response, request
from canvasapi import Canvas

# Canvas API URL
API_URL = "https://canvas.slu.edu"
# Canvas API key (set CANVAS_API_KEY in your environment)
API_KEY = os.getenv("CANVAS_API_KEY")
API_KEY_MISSING = "Canvas API key not set."
CANVAS_REQUEST_FAILED = "Canvas request failed"
NO_COURSE_SELECTED = "No course selected."

app = Flask(__name__)
selected_course = {"id": None, "name": None}


def get_teacher_courses(canvas_client):
    user = canvas_client.get_current_user()
    courses = user.get_courses()
    teacher_courses = []

    for course in courses:
        enrollments = course.get_enrollments(user_id=user.id)
        roles = {enrollment.role for enrollment in enrollments if enrollment.role}
        if roles:
            role_list = ", ".join(sorted(roles))
            if "TeacherEnrollment" in role_list or "TaEnrollment" in role_list:
                teacher_courses.append(course)

    return [{"id": course.id, "name": course.name} for course in teacher_courses]


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    return jsonify({"error": "Server error", "details": str(error)}), 500

def get_canvas_client():
    if not API_KEY:
        return None
    return Canvas(API_URL, API_KEY)

@app.route("/setApiKey", methods=["POST", "OPTIONS"])
def set_api_key():
    if request.method == "OPTIONS":
        return make_response("", 204)
    payload = request.get_json(silent=True) or {}
    api_key = payload.get("apiKey")
    if not api_key:
        return jsonify({"error": "Missing apiKey."}), 400
    global API_KEY
    API_KEY = api_key
    return jsonify({"ok": True})

@app.route("/clearApiKey", methods=["POST", "OPTIONS"])
def clear_api_key():
    if request.method == "OPTIONS":
        return make_response("", 204)
    global API_KEY
    API_KEY = None
    return jsonify({"ok": True})


@app.route("/getAssignments", methods=["GET", "OPTIONS"])
def assignments():
    if request.method == "OPTIONS":
        return make_response("", 204)

    canvas = get_canvas_client()
    if not canvas:
        return jsonify({"error": API_KEY_MISSING}), 400
    course_id = request.args.get("courseId") or selected_course.get("id")
    if not course_id:
        return jsonify({"error": "No course selected."}), 400
    course = canvas.get_course(course_id)
    assignments = course.get_assignments(
        include=["submission_types", "points_possible", "due_at", "unlock_at", "lock_at", "published"]
    )
    assignment_list = []
    for assignment in assignments:
        assignment_list.append(
            {
                "id": getattr(assignment, "id", None),
                "name": getattr(assignment, "name", None),
                "submission_types": getattr(assignment, "submission_types", None) or [],
                "points_possible": getattr(assignment, "points_possible", None),
                "due_at": getattr(assignment, "due_at", None),
                "unlock_at": getattr(assignment, "unlock_at", None),
                "lock_at": getattr(assignment, "lock_at", None),
                "published": getattr(assignment, "published", None),
            }
        )
    return jsonify({"assignments": assignment_list})

@app.route("/courses", methods=["GET", "OPTIONS"])
def courses():
    if request.method == "OPTIONS":
        return make_response("", 204)

    canvas = get_canvas_client()
    if not canvas:
        return jsonify({"error": API_KEY_MISSING}), 400
    try:
        return jsonify({"courses": get_teacher_courses(canvas)})
    except Exception as error:
        error_text = str(error)
        status_code = 500
        if "401" in error_text or "Unauthorized" in error_text:
            status_code = 401
        return jsonify({"error": CANVAS_REQUEST_FAILED, "details": error_text}), status_code


@app.route("/selected-course", methods=["POST", "OPTIONS"])
def update_selected_course():
    if request.method == "OPTIONS":
        return make_response("", 204)

    payload = request.get_json(silent=True) or {}
    selected_course["id"] = payload.get("courseId")
    selected_course["name"] = payload.get("courseName")
    return jsonify({"ok": True, "selectedCourse": selected_course})


@app.route("/selected-course", methods=["GET"])
def read_selected_course():
    return jsonify({"selectedCourse": selected_course})

def normalize_due_at(value):
    if not value:
        return None
    if len(value) == 10:
        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            return datetime.combine(
                parsed_date, time(5, 59), tzinfo=timezone.utc
            ).isoformat().replace("+00:00", "Z")
        except ValueError:
            return value
    return value

def build_quiz_question(question):
    question_type = (question.get("type") or "").strip().lower()
    valid_types = {
        "multiple_choice_question",
        "essay_question",
        "true_false_question",
        "short_answer_question",
    }
    if question_type not in valid_types:
        question_type = "essay_question"
    answers_text = question.get("answers") or ""
    answers = [
        answer.strip()
        for answer in answers_text.split(",")
        if answer.strip()
    ]
    payload = {
        "question_name": question.get("title") or "Question",
        "question_text": question.get("content") or "",
        "question_type": question_type,
    }
    if question_type == "multiple_choice_question" and answers:
        payload["answers"] = [
            {"text": answer, "weight": 100 if index == 0 else 0}
            for index, answer in enumerate(answers)
        ]
    elif question_type == "true_false_question":
        is_true = answers_text.strip().lower() in {"true", "t", "yes", "1"}
        payload["answers"] = [
            {"text": "True", "weight": 100 if is_true else 0},
            {"text": "False", "weight": 0 if is_true else 100},
        ]
    return payload

@app.route("/postAssignment", methods=["POST", "OPTIONS"])
def post_assignment():
    if request.method == "OPTIONS":
        return make_response("", 204)

    canvas = get_canvas_client()
    if not canvas:
        return jsonify({"error": API_KEY_MISSING}), 400
    payload = request.get_json(silent=True) or {}
    course_id = payload.get("courseId") or selected_course.get("id")
    assignment_name = payload.get("assignmentNameInput")
    assignment_description = payload.get("assignmentDescriptionInput")
    assignment_points = payload.get("assignmentPointsInput")
    assignment_due = payload.get("assignmentDueDateInput")
    assignment_start = payload.get("assignmentStartInput")
    submission_type = payload.get("submissionType") or "online"
    publish_immediately = payload.get("publishImmediately")
    if publish_immediately is None:
        publish_immediately = True
    
    if not course_id:
        return jsonify({"error": NO_COURSE_SELECTED}), 400

    if assignment_points == "":
        assignment_points = None
    elif assignment_points is not None:
        try:
            assignment_points = float(assignment_points)
        except ValueError:
            return jsonify({"error": "Invalid points value."}), 400

    if assignment_due == "":
        assignment_due = None

    assignment_due = normalize_due_at(assignment_due)
    assignment_start = normalize_due_at(assignment_start)
    submission_type_map = {
        "online": ["online_upload"],
        "none": ["none"],
        "on_paper": ["on_paper"],
    }
    submission_types = submission_type_map.get(submission_type, ["online_upload"])

    try:
        course = canvas.get_course(course_id)
        assignment_payload = {
            'name': assignment_name,
            'submission_types': submission_types,
            'points_possible': assignment_points,
            'description': assignment_description,
            'due_at': assignment_due,
            'unlock_at': assignment_start,
            'lock_at': assignment_due,
            'published': publish_immediately
        }
        if submission_types == ["online_upload"]:
            assignment_payload["allowed_extensions"] = ['docx', 'doc', 'pdf']
        new_assignment = course.create_assignment(assignment_payload)
        return jsonify({"ok": True, "assignmentId": new_assignment.id})
    except Exception as error:
        return jsonify({"error": CANVAS_REQUEST_FAILED, "details": str(error)}), 500

@app.route("/postQuiz", methods=["POST", "OPTIONS"])
def post_quiz():
    if request.method == "OPTIONS":
        return make_response("", 204)

    canvas = get_canvas_client()
    if not canvas:
        return jsonify({"error": API_KEY_MISSING}), 400
    payload = request.get_json(silent=True) or {}
    course_id = payload.get("courseId") or selected_course.get("id")
    quiz_title = payload.get("quizTitle") or "Generated quiz"
    questions = payload.get("questions") or []
    publish_immediately = payload.get("publishImmediately")
    if publish_immediately is None:
        publish_immediately = True
    if not course_id:
        return jsonify({"error": NO_COURSE_SELECTED}), 400
    if not questions:
        return jsonify({"error": "No quiz questions provided."}), 400

    try:
        course = canvas.get_course(course_id)
        quiz = course.create_quiz({
            "title": quiz_title,
            "published": bool(publish_immediately),
        })
        for question in questions:
            quiz.create_question(question=build_quiz_question(question))

        return jsonify({"ok": True, "quizId": quiz.id})
    except Exception as error:
        return jsonify({"error": CANVAS_REQUEST_FAILED, "details": str(error)}), 500

@app.route("/togglePublish", methods=["POST", "OPTIONS"])
def toggle_publish():
    if request.method == "OPTIONS":
        return make_response("", 204)
    payload = request.get_json(silent=True) or {}
    assignment_id = payload.get("assignmentId")
    course_id = payload.get("courseId") or selected_course.get("id")
    published = payload.get("published")
    if assignment_id is None or published is None or not course_id:
        return jsonify({"error": "Missing assignmentId, published, or courseId."}), 400
    if isinstance(published, str):
        published_value = published.strip().lower() in {"true", "1", "yes"}
    else:
        published_value = bool(published)
    try:
        canvas = get_canvas_client()
        if not canvas:
            return jsonify({"error": API_KEY_MISSING}), 400
        course = canvas.get_course(course_id)
        assignment = course.get_assignment(int(assignment_id))
        assignment.edit(assignment={"published": published_value})
        return jsonify({"ok": True, "assignmentId": assignment.id})
    except Exception as error:
        return jsonify({"error": CANVAS_REQUEST_FAILED, "details": str(error)}), 500

@app.route("/deleteAssignment", methods=["POST", "OPTIONS"])
def delete_assignment():
    if request.method == "OPTIONS":
        return make_response("", 204)
    payload = request.get_json(silent=True) or {}
    assignment_id = payload.get("assignmentId")
    course_id = payload.get("courseId")
    try:
        canvas = Canvas(API_URL, API_KEY)
        course = canvas.get_course(course_id)
        assignment = course.get_assignment(int(assignment_id))
        assignment.delete()
        return jsonify({"ok": True})
    except Exception as error:
        return jsonify({"error": "Canvas request failed", "details": str(error)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)