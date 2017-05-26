import os
import glob
import subprocess
import time

images_path = '/var/lib/motion/'

def uploadToS3(filePath):
    return os.system("aws s3 cp "+filePath+" s3://nthu105062548/hackthon/catchedfiles/")

def rekFace(fileName):
    s = ("aws rekognition search-faces-by-image"
        " --image '{\"S3Object\":{\"Bucket\":\"nthu105062548\",\"Name\":\"hackthon/catchedfiles/"+fileName+"\"}}'"
        " --collection-id \"hackthon\""
        " --region us-east-1  --profile default")
    result =  subprocess.check_output(s,shell=True)
    small=2147483647
    ans = "NULL"
    roger = result.find("roger")
    duck = result.find("duck")
    silver = result.find("silver")
    print "roger %d duck %d silver %d" % (roger,duck,silver)
    if roger!=-1 and roger<small:
        samll = roger
        ans = "roger"
    if duck!=-1 and duck<small:
        small = duck
        ans = "duck"
    if silver!=-1 and silver<small:
        small = silver
        ans = "silver"
    return ans

print "start Catching!!!!"

while True:
    #time.sleep(5)
    list_of_files = glob.glob(images_path+'*') 
    latest_file = max(list_of_files, key=os.path.getctime)
    print "Neweast File "+latest_file+" catched"
    if(uploadToS3(latest_file)!=0):
        print "upload file faild"

    file_name =  os.path.basename(latest_file)
    try:
        user = rekFace(file_name)
        if user!="NULL":
            print "catch User "+user
            os.system("curl -d \""+user+"\" https://lpvd07fec9.execute-api.us-east-1.amazonaws.com/prod/API-to_lambda")
    except:
        print "No face"



