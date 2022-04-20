import os,io
from google.cloud import vision

def api(folder_path, image_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']=r'C:\Users\tusht\Downloads\classmanager-student-teacher-portal-master\classmanager-student-teacher-portal-master\classmanager\media\checker\ServiceAccountToken.json'
    client=vision.ImageAnnotatorClient()
    FILE_PATH=os.path.join(folder_path,image_path)

    with io.open(FILE_PATH,'rb') as image_file:
        content= image_file.read()

    image=vision.Image(content=content)
    response = client.document_text_detection(image=image)
    doctext1=response.full_text_annotation.text
    return doctext1

