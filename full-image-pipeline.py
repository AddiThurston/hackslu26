import os
from google.cloud import vision
from google import genai
from GeometricFitter import GeometricFitter
import cv2 as cv
import io
from PIL import Image


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'hackslu26-test\hackslu26-488119-65e1274a9946.json'



def scan_image(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    if response.full_text_annotation:
        print("text extracted")
        output = response.full_text_annotation.text
        return output
    else:
        return False

    
client = genai.Client()
    
if __name__ == "__main__":

    image = cv.imread("hackslu26-test\\test-photos\\pipelinetest1.jpg")
    
    fittedImage = GeometricFitter.FitImage(image, 50, 150)

    fittedImageJpeg = Image.fromarray(fittedImage, 'RGB')
    fittedImageJpeg.save("fitted_image.jpg")


    input = scan_image("fitted_image.jpg")


    if input != False:
        ai_output = client.models.generate_content(
        model="gemini-2.5-flash", contents= input + ''' given this text, can you break everything off into segments separated by a '|' 
        that can be easily parsed so it can be processed and sent to a canvas API. 
        i need, in order, the course name, an assignment name (come up with one if it isn't given), the assignment type (if this isn't given,
        choose from the options 'Assignment', 'Reading', or 'Discussion'), a description for the assignment for the students (this will display on canvas for the assignment),
        a point value (if one is given. leave blank if pass/fail),
        a start date (if one is given, formatted MM/DD), 
        a due date (if one is given, formatted MM/DD).  ''')
        print(ai_output.text)
    else:
        print("No text found in the image.")