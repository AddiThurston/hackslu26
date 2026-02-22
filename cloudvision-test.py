import os
from flask import Flask, jsonify, request, make_response
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "hackslu26-test\\hackslu26-488119-65e1274a9946.json"

app = Flask(__name__)


def scan_image_bytes(content):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    if response.error.message:
        raise RuntimeError(f"{response.error.message}")
    if response.full_text_annotation:
        return response.full_text_annotation.text
    return ""


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
    content = image_file.read()
    text = scan_image_bytes(content)
    return jsonify({"text": text})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)