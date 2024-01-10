import argparse
from enum import Enum
import re
import io
import os
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import automl
from PIL import Image, ImageDraw, ImageEnhance
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d as conv2
import urllib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
#from skimage import color, data, restoration
#from skimage.filters import threshold_local
#import imutils
import math
#import glob
from scipy import ndimage
import json
from PIL import Image, ImageEnhance
from PIL import Image
import requests
from io import BytesIO
import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True




from google.cloud import vision
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Salary Dost-a9e341ace734 - Copy.json"
client = vision.ImageAnnotatorClient()


VALID_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
]

def valid_url_extension(url, extension_list=VALID_IMAGE_EXTENSIONS):
    # http://stackoverflow.com/a/10543969/396300
    return any([url.endswith(e) for e in extension_list]) 


def label(img):

    project_id = "salary-dost"
    model_id = "ICN4622096194519171072"

    prediction_client = automl.PredictionServiceClient()

    # Get the full path of the model.
    model_full_id = prediction_client.model_path(
        project_id, "us-central1", model_id
    )


    content=img
    imgByte = io.BytesIO()

    content.save(imgByte, format='jpeg')
    imgByte = imgByte.getvalue()

    image = automl.types.Image(image_bytes=imgByte)
    payload = automl.types.ExamplePayload(image=image)

    # params is additional domain-specific parameters.
    # score_threshold is used to filter the result
    # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#predictrequest
    params = {"score_threshold": "0.8"}

    response = prediction_client.predict(model_full_id, payload, params,timeout=30.0)
    #print("Prediction results:")
    for result in response.payload:
        #print("Predicted class name: {}".format(result.display_name))
        #print("Predicted class score: {}".format(result.classification.score))
        res= result.display_name

    return res




def resize(image):
    h, w, c = image.shape
    factor = min(1, float(1024.0 /h))
    height = int(h*factor)
    width = int(w*factor)
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)
    return resized



def gray_scale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def enhance(image):
    #image = Image.open(image)
    enhancer = ImageEnhance.Sharpness(image)
    img_sharp = enhancer.enhance(1.7)
    enh = ImageEnhance.Contrast(img_sharp)
    contrast = enh.enhance(1.7)
    return contrast





def f1(y):
    y = y.replace("-",":")
    y=re.sub("[^A-Za-z0-9:/.\n#, ]", "", y.strip())
    y=y.strip().splitlines()
    y = [x for x in y if x != " " and x!="  " and x!=""]
    y = [x for x in y if x!="www"]
    y = [x for x in y if x!="w ww"]
    y = [x for x in y if x!='1']
    y = [x for x in y if x!="/"]
    y = [x for x in y if x!=',']
    y = [x for x in y if x!=':']
    y = [x for x in y if x != '   ' and x!="    "]
    y = [x.strip() for x in y]
  
    return y





def pan(z):
    global m
    for i in range(len(z)):
        if "GOVT" in z[i]:
            index = i
            m=z[i+1:]
            break
    for i in range(len(m)):
        if "INCOME TAX" in m[i]:
            index = i
            m=m[i+1:]
            break
    for i in range(len(m)):
        if "OF INDIA" in m[i]:
            index = i
            m=m[i+1:]
            break
    for i in range(len(m)):
        if "Application" in m[i]:
            index = i
            m=m[:i]
            break
    for i in range(len(m)):
        if "Banking" in m[i]:
            index = i
            m=m[:i]
            break
    for i in range(len(m)):
        if "Digital" in m[i]:
            index = i
            m=m[:i]
            break
    for i in range(len(m)):
        if "Signature" in m[i]:
            index = i
            m=m[:i]
            break
    for i in range(len(m)):
        if 'www' in m[i]:
            m.remove(m[i])
            break
    return m





def pan_no(z):
    for i in range(len(z)):
        if 'Permanent' in z[i] or 'Account Number' in z[i] or 'Paimaneat' in z[i]:
            if i == len(z)-1:
                m = ''
            else:
                m = z[i+1]
            break
        else:
            m =''
  
    return m





def fn_name(z):
    for i in range(len(z)):
        if 'Name' in z[i]:
            m = z[i+1]
            break
        else:
            m = z[0]
    return m





def fn_father(z):
    for i in range(len(z)):
        if 'Father' in z[i] or 'Fhers' in z[i] or 'Fr3' in z[i]:
            m = z[i+1]
            break
        else:
            m = z[1]
    return m




def date(z):
    for i in range(len(z)):
        if 'Date' in z[i] or 'Birth' in z[i]:
            if i == len(z)-1:
                m = z[i]
            else:
                m = z[i+1]
            break
        else:
            m = z[2]
    return m




@app.route('/', methods=['GET'])
def home():
    return '''<h1>IP</h1>
<p>Extract user details</p>'''


@app.route('/api/v1/resources/pan/all', methods=['GET'])
def api_all():
    return jsonify(pan)


@app.route('/api/v1/resources/pan', methods=['GET'])
def api_id():
    
    query_parameters = request.args
    
    url=query_parameters.get('url')
    #validating url

    
    if 'url' not in request.args:
        return "Error: No url provided. Please specify a url.--->/api/v1/resources/pan?url=url"
    #else:

    req = Request(url)
    try:
        res = urlopen(req)
    except HTTPError as e:
        a="The server couldn't fulfill the request. Error code: "+str(e.code)
        return a
    except URLError as e:
        b='We failed to reach a server. Reason: '+str(e.reason)
        return b

    else:
        # everything is fine
        

        if valid_url_extension(url)==False:
            return "Please enter a valid URL to an image--> .jpg .jpeg .png"

        else:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))

            if label(img)!="pan":
                return "Please enter the url for pan image with extension--> .jpg .jpeg .png"

            else:                 
                           
                contrast=enhance(img)
                resized = resize(np.float32(contrast))
                grayed = gray_scale(resized)
                _, encoded = cv2.imencode('.jpeg', grayed)
                imgByteArr = encoded.tobytes()
                #skewed = skewing(grayed)


                #imgByteArr = io.BytesIO()
                #grayed.save(imgByteArr, format='jpeg')
                #imgByteArr = imgByteArr.getvalue()
        
                image = vision.types.Image(content=imgByteArr)
                response = client.text_detection(image=image)
                texts = response.text_annotations


                x = []
                for text in texts:
                    tex = text.description
                    x.append(tex)

                doc_text = x[0]
                
        
        
                doc_text = f1(doc_text)
                doc_text=pan(doc_text)

                pan_number=pan_no(doc_text)                  
                name = fn_name(doc_text)
                name = re.sub(r'[0-9\W_]',' ',name)
                           
                father_name=fn_father(doc_text)
                father_name = re.sub(r'[0-9\W_]',' ',father_name)                  
        
                dob=date(doc_text)
                dob = re.sub(r'[A-Za-z\s+_]','',dob) 

                d=[{
                    "Name": name,
                    "Father's_Name":father_name,
                    "DOB": dob,
                    "Pan_number":pan_number
                    }]                  
                         

    

    
    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
                return jsonify(d)

app.run()



   
