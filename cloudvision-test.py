import os
from google.cloud import vision

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'hackslu26-test\hackslu26-488119-7c93c72fded4.json'

def scan_image(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    if response.full_text_annotation:
        print("text extracted")
        print(response.full_text_annotation.text)
    else:
        print("No text detected.")
    if response.error.message:
        raise Exception(f'{response.error.message}')
    
if __name__ == "__main__":
    scan_image('hackslu26-test\\first_real_test.jpg')