import os
from flask import Flask, jsonify, request, make_response
from google.cloud import vision
from google import genai

import io
from pdf2image import convert_from_bytes

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'hackslu26-test\\hackslu26-488119-65e1274a9946.json'
POPPLER_PATH = os.getenv("POPPLER_PATH", r"C:\Program Files\poppler-25.12.0\Library\bin")

app = Flask(__name__)

def scan_image(image_path):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_path)
    response = client.text_detection(image=image)
    if response.full_text_annotation:
        print("text extracted")
        output = response.full_text_annotation.text
        return output
    else:
        return False
    
client = genai.Client()
MODEL_NAME = "gemini-2.5-flash"

def normalize_quiz_output(text):
    parts = [part.strip() for part in text.split("|") if part.strip()]
    if len(parts) < 4:
        parts += [""] * (4 - len(parts))
    return "|".join(parts[:4])

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.route("/scan", methods=["POST", "OPTIONS"])
def scan():
    if request.method == "OPTIONS":
        return make_response("", 204)

    if "image" not in request.files:
        return jsonify({"error": "Missing image file"}), 400

    image_file = request.files["image"]
    image_path = image_file.read()
    text = scan_image(image_path)
    if text != False:
        ai_output = client.models.generate_content(
        model=MODEL_NAME, contents= text + ''' given this text, can you break everything off into segments separated by a '|' 
        that can be easily parsed so it can be processed and sent to a canvas API. 
        i need, in order, the course name, an assignment name (come up with one if it isn't given), the assignment type (if this isn't given,
        choose from the options 'Assignment', 'Reading', or 'Discussion'), a description for the assignment for the students (this will display on canvas for the assignment),
        a point value (if one is given. leave blank if pass/fail),
        a start date (if one is given, formatted yyyy-MM-dd and you can assume the year is 2026 if not given), 
        a due date (if one is given, formatted yyyy-MM-dd and you can assume the year is 2026 if not given).  ''')
        text = ai_output.text
    else:
        text = "No text found in the image."
    return jsonify({"text": text})

@app.route("/givePrompt", methods=["POST", "OPTIONS"])
def give_prompt():
    if request.method == "OPTIONS":
        return make_response("", 204)
    if "assignmentPrompt" not in request.json:
        return jsonify({"error": "Missing assignment prompt"}), 400

    assignment_prompt = request.json["assignmentPrompt"]
    ai_output = client.models.generate_content(
        model=MODEL_NAME, contents= assignment_prompt + ''' given this text, can you break everything off into segments separated by a '|' 
        that can be easily parsed so it can be processed and sent to a canvas API. 
        i need, in order, the course name, an assignment name (come up with one if it isn't given), the assignment type (if this isn't given,
        choose from the options 'Assignment', 'Reading', or 'Discussion'), a description for the assignment for the students (this will display on canvas for the assignment),
        a point value (if one is given. leave blank if pass/fail),
        a start date (if one is given, formatted yyyy-MM-dd and you can assume the year is 2026 if not given), 
        a due date (if one is given, formatted yyyy-MM-dd and you can assume the year is 2026 if not given).  ''')
    return jsonify({"text": ai_output.text})

@app.route("/makeQuiz", methods=["POST", "OPTIONS"])
def make_quiz():
    if request.method == "OPTIONS":
        return make_response("", 204)
    pdf_file = request.files.get("lectureNotes")
    if not pdf_file:
        return jsonify({"error": "Missing lecture notes file"}), 400

    pdf_bytes = pdf_file.read()
    if not pdf_bytes:
        return jsonify({"error": "Empty lecture notes file"}), 400

    pages = convert_from_bytes(pdf_bytes, fmt="jpeg", poppler_path=POPPLER_PATH)
    extracted_text = ""
    for page in pages[:20]:
        buffer = io.BytesIO()
        page.save(buffer, format="JPEG")
        page_text = scan_image(buffer.getvalue())
        if page_text:
            extracted_text += page_text + " "

    if extracted_text == "":
        return jsonify({"error": "No text found in the PDF."}), 400

    full_text = ""
    # ADDISON! THIS VARIABLE BELOW ME!!!! IT'S THE NUMBER OF QUIZ QUESTIOOOOONNNNNNSSSSSS!!!!!!!!!!!!!!!
    quiz_question_number_as_in_the_number_of_quiz_questions_for_anyone_who_might_be_wondering_also_quiz_is_short_for_quizzical = 5
    for _ in range(quiz_question_number_as_in_the_number_of_quiz_questions_for_anyone_who_might_be_wondering_also_quiz_is_short_for_quizzical):
        ai_output = client.models.generate_content(
            model=MODEL_NAME, contents= extracted_text + '''   
            for each parameter im giving, separate each with '|' 
            that can be easily parsed so it can be processed and sent to a canvas API. this will result in ONE question.
            I need, in order, the name of the question, the content of the question (what the question is asking),
            the question type (chosen from one of the following: 'multiple_choice_question', 'essay_question', 'true_false_question', 'short_answer_question'),
            and the potential answers for the question (if it's a multiple choice question, make the first of the four answers the correct one. if it's true or false, input the proper boolean. 
            if it's essay or a short answer question, leave the answer blank. If blank, ensure that the field is still separated by a '|'
            It is very important that the fields are separated by a '|' and that the fields are in the order specified.
            )  ''')
        full_text += normalize_quiz_output(ai_output.text) + "|"
    return jsonify({"quiz": full_text})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)