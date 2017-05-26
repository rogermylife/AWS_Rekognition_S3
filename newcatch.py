import os
import glob
import subprocess
import time
import boto3
import setting

images_path = '/var/lib/motion/'
s3 = boto3.resource('s3')
rek = boto3.client('rekognition')

def uploadToS3(file_path):
    file_name =  os.path.basename(latest_file)
    s3.Object(setting.BUCKET_NAME,setting.BUCKET_FOLDER+file_name).upload_file(file_path)

def rekFace(file_name):
    result = rek.search_faces_by_image(
        CollectionId='hackthon',
        FaceMatchThreshold=95,
        Image={
            'S3Object': {
                'Bucket': setting.BUCKET_NAME,
                'Name': setting.BUCKET_FOLDER+file_name
            },
        },
        MaxFaces=5,
    )
    image_id = 'NULL'
    for face in result['FaceMatches']:
        face = face['Face']
        print face
        image_id = face.get('ExternalImageId', 'NULL')
        #print face['ExternalImage']
        if image_id != 'NULL':
            break
    return image_id

print "start Catching!!!!"

while True:
    #time.sleep(5)
    list_of_files = glob.glob(images_path+'*') 
    latest_file = max(list_of_files, key=os.path.getctime)
    print "Neweast File "+latest_file+" catched"
    uploadToS3(latest_file)
    print "upload file done"

    file_name =  os.path.basename(latest_file)
    try:
        user = rekFace(file_name)
        if user!="NULL":
            print "catch User "+user
            os.system("curl -d \""+user+"\" https://lpvd07fec9.execute-api.us-east-1.amazonaws.com/prod/API-to_lambda")
    except:
        print "No face"



