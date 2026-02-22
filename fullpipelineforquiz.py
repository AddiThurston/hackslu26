import os
from google.cloud import vision
from google import genai
from GeometricFitter import GeometricFitter
import cv2 as cv
import io
from PIL import Image
from pdf2image import convert_from_path


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
        return " "

    
client = genai.Client()
    
if __name__ == "__main__":

    # image = cv.imread("hackslu26-test\\test-photos\\pipelinetest1.jpg")
    
    # fittedImage = GeometricFitter.FitImage(image, 50, 150)

    # fittedImageJpeg = Image.fromarray(fittedImage, 'RGB')
    # fittedImageJpeg.save("fitted_image.jpg")


    # input = scan_image("fitted_image.jpg")

    folder_path = "hackslu26-test\\qwertyuioplkjhgfdsa"

    if not os.path.exists(folder_path):
        os.mkdir(folder_path) 
    else:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            os.remove(file_path)



    convert_from_path("hackslu26-test\\test-slideshows\\splitpdf.pdf",
                      output_folder="hackslu26-test\\qwertyuioplkjhgfdsa", fmt='jpg')

    i = 0
    input = ""
    for filename in os.listdir(folder_path):
        if i >= 10:
            break
        i += 1
        file_path = os.path.join(folder_path, filename)
        input += scan_image(file_path) + " "

    if input != "":
        full_text = ""
        #ADDISON! THIS VARIABLE BELOW ME!!!! IT'S THE NUMBER OF QUIZ QUESTIOOOOONNNNNNSSSSSS!!!!!!!!!!!!!!!
        quiz_question_number_as_in_the_number_of_quiz_questions_for_anyone_who_might_be_wondering_also_quiz_is_short_for_quizzical = 5
        for i in range(quiz_question_number_as_in_the_number_of_quiz_questions_for_anyone_who_might_be_wondering_also_quiz_is_short_for_quizzical):
            ai_output = client.models.generate_content(
            model="gemini-2.5-flash", contents= input + '''   
            for each parameter im giving, separate each with '|' 
            that can be easily parsed so it can be processed and sent to a canvas API. this will result in ONE question.
            I need, in order, the name of the question, the content of the question (what the question is asking),
            the question type (chosen from one of the following: 'multiple_choice_question', 'essay_question', 'true_false_question', 'short_answer_question'),
            and the potential answers for the question (if it's a multiple choice question, make the first of the four answers the correct one. if it's true or false, input the proper boolean. 
            if it's essay or a short answer question, leave the answer blank.
            )  ''')
            full_text += ai_output.text + "|"
    else:
        print("No text found in the image.")

    print(full_text)