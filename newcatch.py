import os
import glob
import subprocess
import time
import boto3
import setting
import urllib2
import json

images_path = '/var/lib/motion/'
s3 = boto3.resource('s3')
rek = boto3.client('rekognition')
irsendStr='irsend SEND_ONCE /home/pi/lircd.conf '
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
    list_of_files=[]
    while not list_of_files:
        list_of_files = glob.glob(images_path+'*') 
    latest_file = max(list_of_files, key=os.path.getctime)
    print "Neweast File "+latest_file+" catched"
    uploadToS3(latest_file)
    print "upload file done"
    file_name =  os.path.basename(latest_file)
    os.system("rm -rf /var/lib/motion/*")
    response = urllib2.urlopen("https://azlfh6jc02.execute-api.us-east-1.amazonaws.com/asdf/globalvar")
    resStr = response.read()
    print "Power Response ",resStr
    data = json.loads(resStr)
    try:
        user = rekFace(file_name)
        if user!="NULL":
            print "catch User "+user
            print 'response  ',response.read()
            if data['errorMessage']=="0":
                print 'POWER UP'
                os.system("curl -d '{\"user\":\""+user+"\"}' https://eeppi3k3o9.execute-api.us-east-1.amazonaws.com/prod/api2db")
                print ("curl -d \"{\"user\":\""+user+"\"}\" https://eeppi3k3o9.execute-api.us-east-1.amazonaws.com/prod/api2db")
                dataUser = {
                    'user':user
                }
                req = urllib2.Request('https://ap7xthd885.execute-api.us-east-1.amazonaws.com/lastsee')
                req.add_header('Content-Type','application/json')
                reqqq = urllib2.urlopen(req,json.dumps(dataUser))
                userRes = reqqq.read()
                userResJson = json.loads(userRes)
                number = userResJson['body-json']
                BTN_= " BTN_"
                numberCmd=""
                for n in str(number):
                    numberCmd+=BTN_+n
                print 'Turn '+number+' '+numberCmd
                os.system(irsendStr+'KEY_POWER')
                postUrl = 'https://eeppi3k3o9.execute-api.us-east-1.amazonaws.com/prod/api2db'
                os.system('curl -d "{\\"action\\":\\"turn '+number+'\\"}" '+postUrl)
                os.system(irsendStr+numberCmd)

    except:
        print "No face"



