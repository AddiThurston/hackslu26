import os
from flask import Flask, jsonify, request, make_response
from google.cloud import vision
from google import genai

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'hackslu26-test\\hackslu26-488119-65e1274a9946.json'

app = Flask(__name__)

def scan_image(image_path):
    client = vision.ImageAnnotatorClient()
    #with open(image_path, 'rb') as image_file:
    #    content = image_file.read()
    image = vision.Image(content=image_path)
    response = client.text_detection(image=image)
    if response.full_text_annotation:
        print("text extracted")
        output = response.full_text_annotation.text
        return output
    else:
        return False
    
client = genai.Client()

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
        model="gemini-2.5-flash", contents= text + ''' given this text, can you break everything off into segments separated by a '|' 
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
    
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)