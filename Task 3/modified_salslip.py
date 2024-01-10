
#!/usr/bin/env python
# coding: utf-8


#importing libraries
import re
import PIL
from PIL import Image, ImageDraw, ImageEnhance
import cv2
import fitz
from scipy import ndimage
import numpy as np
from urllib.request import urlretrieve
import urllib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
#import pyplot as plt
import matplotlib.pyplot as plt
import img2pdf
import os
import requests
import numpy as np
import math
from io import BytesIO
import pytesseract
from pytesseract import TesseractError
from pdf2image import convert_from_path
import flask
from flask import request, jsonify
from flask import Flask, request, redirect, url_for, flash, jsonify
from flask import Flask
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

app = Flask(__name__)


pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

#app = flask.Flask(__name__)
#app.config["DEBUG"] = True
#app = Flask(__name__)


VALID_URL_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
]


def valid_url_extension(url, extension_list=VALID_URL_EXTENSIONS):
    # http://stackoverflow.com/a/10543969/396300
    return any([url.endswith(e) for e in extension_list]) 


#gray_scaling

def gray_scale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

#sharpening

def sharpness(image):
    enhancer = ImageEnhance.Sharpness(image)
    img_sharp = enhancer.enhance(2)
    return img_sharp

#increasing contrast

def contrast(image):
    enh = ImageEnhance.Contrast(image)
    contra = enh.enhance(3.0)
    return contra
    

#skewing

def skewing(image):
    image = image.astype(np.uint8)
    img_edges = cv2.Canny(image, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)
    angles = []
    for x1, y1, x2, y2 in lines[0]:
        cv2.line(np.float32(image), (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)
    median_angle = np.median(angles)
    img_rotated = ndimage.rotate(image, median_angle)
    print("Angle is {}".format(median_angle))
    
    return img_rotated

#preprocessing main

def prep(pic):
    sharp = sharpness(pic)
    cont = contrast(sharp)
    resized = np.float32(cont)
    grayed = gray_scale(resized)
    #skewed = skewing(grayed)
    
    return grayed


def f1(y):
    #y = y.replace("    "," ")
    #y = y.replace("   ","\n")
    y=y.strip().splitlines()
    y=[re.sub("[^A-Za-z0-9-:)(./\n#, ]", "", x.strip()) for x in y]
    y=[re.sub(r'[^\x00-\x7f]',r' ', x) for x in y]
    #y=y.strip().splitlines()
    y = [x.strip() for x in y]
    y = [x.replace('    ','\n') for x in y]
    #src_str  = re.compile("Name of the employee", re.IGNORECASE)

 
    y=[re.compile("Name of the employee", re.IGNORECASE).sub("Name",x) for x in y]
    y=[re.compile("Namo", re.IGNORECASE).sub("Name",x) for x in y]
    y = [x.replace('Nama','Name') for x in y]
    y = [x.replace('Name of the employee','Name') for x in y]
    #y = [x.replace('Name of Employee','Name') for x in y]

    
    #y = [x.replace('NAME','Name') for x in y]
    y = [x.replace('Name:','Name') for x in y]
    #y = [x.replace('name','Name') for x in y]
    y = [x.replace(' OF OFFICIAL','') for x in y]

    y = [re.compile('PAY SLIP', re.IGNORECASE).sub("Payslip",x) for x in y]

    y = [re.compile('islip', re.IGNORECASE).sub("Payslip",x) for x in y]
    #y = [x.replace('Pay slip','Payslip') for x in y]
    
    y = [x.replace('AIC','A/C') for x in y]
    y = [x.replace('Alc no','A/C No') for x in y]
    y = [x.replace('Acc no','A/C No') for x in y]
    y = [x.replace('Ac/No','A/C No') for x in y]
    y = [x.replace('AC No','A/C No') for x in y]
    y = [re.compile('ACNO', re.IGNORECASE).sub("A/C No",x) for x in y]
    y = [re.compile('A/e', re.IGNORECASE).sub("A/C ",x) for x in y]
    y = [re.compile('AIG No', re.IGNORECASE).sub("A/C No",x) for x in y]
    
    y = [x for x in y if len(x) != 1 ]
    
    y = [x for x in y if x != " " and x!="  " and x!=""]
    y = [x for x in y if x != '   ' and x!="    "]
    y = [x for x in y if x != ',']
    y = [x for x in y if x != ':']
    y = [x.replace("\n\n"," ") for x in y]
    y = [x.replace("\n "," ") for x in y]
    #y = [x.replace("\n"," : ") for x in y]
     

    return y




def company_name(z):
    #comp=z[0]
    global flag
    flag=0
    for i in range(0,len(z)):
        comp=z[i]
        
        if "limited" in comp.lower() or "ltd" in comp.lower() or "agency" in comp.lower() or "private" in comp.lower():
            if "bank" not in comp.lower():
                flag=1
                break
            else:
                flag=0
                continue
        else:
            flag=0
            continue
            
        
    
    if flag==0:
        for i in range(0,5):
            comp=z[i]
            
            if "payslip" not in comp.lower() and "name" not in comp.lower() and "first" not in comp.lower():
                n=0
                for j in comp:
                    if j.isdigit()==True:
                        n=n+1
                
                if n==0:
                    break
                else:
                    continue
                
                    
            else:
                continue
        
        
    return comp.strip()      




def name_cus(z):
    global n

    for i in range(len(z)):
        if z[i].lower()=="name" or z[i].lower()=="emp name" or z[i].lower()=="employee name" or z[i].lower()=="empcode/name":
            n=z[i+1]
            return n
            break
            
        elif "name" in z[i].lower() or "employee name" in z[i].lower() or "emp name" in z[i].lower() or "of employee" in z[i].lower():
            index=z[i].lower().index("name")
            if "bank" not in z[i].lower():
                
                if len(z[i][index+4:].strip())<3:
                    n=z[i+1] 
                    return n
                    break   

                else:
                    n=z[i][index+4:]
                    return n
                    break

            else:

                n=bank_in_name(z[i],z)
                n=re.compile('name', re.IGNORECASE).sub("",n).strip()
                return n
                break
            
                
        else:
        
            if i==len(z)-1:
                n=""
                return n
                break
            else:
                continue
                
    #return n#.strip()

def bank_in_name(s,z):
    global ind
    #if "bank" in s.lower():
    ind=s.lower().index("bank")
    if s[:ind].strip()!="":
        return s[:ind].strip()
    else:
        for i in range(len(z)):
            if "name" in z[i].lower() and "bank" not in z[i].lower():
                ind=z[i].lower().index("name")
                if len(z[i][ind+4:].strip())<3:
                    n=z[i+1] 
                    return n
                    break   

                else:
                    n=z[i][ind+4:]
                    return n
                    break
            else:
                return ""
        
    
    
    #return s[:ind].strip()
        
 
            
#return bank
def bank_name(z):
    global bank
    #bank==""
    for i in range(0,len(z)):
        if "bank name" in z[i].lower():
            ind=z[i].lower().index("bank name")
            
            if len(z[i][ind+9:].strip())<3:
                bank=z[i+1] 
                return bank
                break
            else:
                bank=z[i][ind+9:]
                return bank
                break
            
        else:
            if i==len(z)-1:
                bank=""
                #return bank
                break
            else:
                continue
        
        
    if bank=="":
        for i in range(0,len(z)):
    
            if z[i].lower()=="bank name" or z[i].lower()=="bank name:" or z[i].lower()=="bank" or z[i].lower()=="bank:":
                bank=z[i+1]
                
                return bank
                break
            
            
            elif "bank" in z[i].lower() or "employee bank" in z[i].lower() or "pay mode" in z[i].lower():
                words=["date","ac","acc","acc no","a/c","account","details","number"]
                if not any(word in z[i].lower() for word in words):
                
                    if len(z[i])<=9:
                        bank=z[i]+" "+z[i+1]
                    else:
                        bank=z[i]
                    
                    return bank
                    break
            
            
            else:
                if i==len(z)-1:
                    bank=""
                    return bank
                    break
                else:
                    continue
        
        



def account_number(z):
    global ac,index
    for i in range(0,len(z)):
        l1=["pf","accounts","name","date","eps","accountant"]
        l2=["bank a/c no","a/c no","account","a/c","number","ac no.","acc ","acc no"]
        
        if not any(word in z[i].lower() for word in l1) and any(word in z[i].lower() for word in l2):       
        #if (("pf" not in z[i].lower() and "accounts" not in z[i].lower()) and ("name" not in z[i].lower() and "date" not in z[i].lower())) and ("bank a/c no" in z[i].lower() or "a/c no" in z[i].lower() or "a/c" in z[i].lower() or "account" in z[i].lower() or "acc " in z[i].lower() or "ac no." in z[i].lower()) :
            
            if len(z[i])<18:
                ac=z[i]+z[i+1]
            else:
                ac=z[i]       
            
            break
            
        elif ("bank account" in z[i].lower() or "a/c no" in z[i].lower() or "bank details" in z[i].lower()) and "date" not in z[i].lower():
            if len(z[i])<18:
                ac=z[i]+z[i+1]
            else:
                ac=z[i]  
            if "bank name" in ac.lower():
                if ac.lower().index("bank name")>10:
                    ac=ac[:ac.lower().index("bank name")]
                else:
                    ac=ac[ac.lower().index("bank"):]
            break
        
        else:
            ac=""
            
    if "acc" in ac.lower():
        ind=ac.lower().index("acc")
    elif "a/c" in ac.lower():
        ind=ac.lower().index("a/c")
    else:
        ind=0

    ac=ac[ind:]
    st1=ac[::-1]
    index=0
    for i in range(len(st1)):
        if st1[i].isdigit()==True:
            index=i
            break
            
    return st1[index:][::-1].strip()
    




#gross salary

def gross_sal(text):
    global sal,index,space
    sal=""
    for j in range(len(text)):
        if 'gross' in text[j].lower() or 'total earnings' in text[j].lower():# or 'deductions' not in text[j].lower():
            if j!=len(text)-1:
                sal = text[j]+" "+text[j+1]
                sal = re.sub("[^0-9./, ]", "", sal).strip()
            else:
                sal = text[j]
                sal = re.sub("[^0-9./, ]", "", sal).strip()
                #sal = text[i]+" "+text[i+1]
            break
        else:
            sal = ''
            
        
    if sal=="":
        for j in range(len(text)):
            if 'total' in text[j].lower():# or 'total pay' in text[i].lower():
                if j!=len(text)-1:
                    sal = text[j]+" "+text[j+1]
                    sal = re.sub("[^0-9./, ]", "", sal).strip()
                else:
                    sal = text[j]#sal = text[i]+" "+text[i+1]
                    sal = re.sub("[^0-9./, ]", "", sal).strip()
                break
            else:
                sal = ''
            
    st1=sal[::-1]
    index=0
    
    for i in range(len(st1)):
        if st1[i].isdigit()==True:
            index=i
            break

    st2=st1[index:][::-1].strip()


    return st2
        



#net salary

def net_sal(text):
    global sal1,index1
    sal1=""
    for j in range(len(text)):
        if 'net salary' in text[j].lower() or 'net pay' in text[j].lower() or 'Net' in text[j] or 'NET' in text[j] or 'net paid' in text[j].lower() or "take home pay" in text[j].lower():
            if "tax" not in text[j].lower() and "day" not in text[j].lower(): 
                if j!=len(text)-1:
                    sal1 = text[j]+" "+text[j+1]
                    
                    if "net" in sal1.lower():
                        sal1=sal1[sal1.lower().index("net"):]
                        
                    sal1 = re.sub("[^0-9./, ]", "", sal1).strip()
                    if sal1=="":
                        continue
                    else:
                        break
                    
                    
                else:
                    sal1 = text[j]
                    
                    if "net" in sal1.lower():
                        sal1=sal1[sal1.lower().index("net"):]
                        
                    sal1 = re.sub("[^0-9./, ]", "", sal1).strip()
                    if sal1=="":
                        continue
                    else:
                        break
                
           
            else:
                if j==len(text)-1:
                    sal1= ""
                    break
                else:
                    continue
                        
                        
    st1=sal1[::-1]
    index1=0
    for i in range(len(st1)):
        if st1[i].isdigit()==True:
            index=i
            break
            
    return st1[index1:][::-1].strip()
        
                    

#time period
def time(text):
    global t,index
    for i in range(len(text)):
        if ('month' in text[i].lower() or 'month of' in text[i].lower() or 'for ' in text[i].lower()) and ("current" not in text[i].lower() and "per" not in text[i].lower() and "monthly" not in text[i].lower()):
            if "month" in text[i].lower():
                ind=text[i].lower().index("month")
                if len(text[i][ind+5:].strip())<5:
                    continue
                else:
                    t = text[i]
                    break
                    
            if "for" in text[i].lower():
                ind=text[i].lower().index("for")
                if len(text[i][ind+3:].strip())<4:
                    continue
                else:
                    t = text[i] #+"  "+text[i+1]
                    break
        else:
            t = ''
            
    if t=="":
        for i in range(len(text)):
            if 'salary slip' in text[i].lower() or 'payslip' in text[i].lower() or 'pay slip' in text[i].lower() or 'period' in text[i].lower():
                t = text[i]
                break
            else:
                t=''
            
    
    index=len(t)
    if "month" in t.lower():
        index=t.lower().index("month")
        return t[index:].strip()
    elif "for" in t.lower():
        index=t.lower().index("for")
        return t[index:].strip()
    elif "pay" in t.lower():
        index=t.lower().index("pay")
        return t[index:].strip()
    elif "salary" in t.lower():
        index=t.lower().index("salary")
        return t[index:].strip()
    else:
        index=len(t)
        return t.strip()





def main(pdf):
    try:
        pdf_ = fitz.open(pdf)
        page = pdf_[0]
        page = page.getText("text")
        
        text=page.encode('utf8').decode('ascii', errors='ignore')
        text=f1(text)
        
    except Exception:
        #print("cannot be opened")
        text=""

    return text
    


def pdf_img(pdf):
    pages = convert_from_path(pdf, 500)
    for page in pages:
        page.save('input.jpg', 'JPEG')
    
    
    im = Image.open(r"input.jpg")
    img = prep(im)
    cv2.imwrite("input.png", img)
    
    image = cv2.imread("input.png")
    
    #getting image in the correct orientation
    try:
        angle=int(re.search('(?<=Orientation in degrees: )\d+', pytesseract.image_to_osd(image)).group(0))
        filename = "{}.png".format(os.getpid())
    
        cv2.imwrite(filename,ndimage.rotate(image, angle))
    
        #plt.imshow(ndimage.rotate(image, angle))
    
        text = pytesseract.image_to_string(Image.open(filename),config="-l eng --oem 1 --psm 3")
        text=f1(text)
        os.remove(filename)
        
        return text
    
    except TesseractError as e:
        c=str(e.message)
        text = pytesseract.image_to_string(Image.open("input.png"),config="-l eng --oem 1 --psm 3")
        text=f1(text)
        #os.remove(filename)
        print(c) 
        return text
        
        



def img(url):
    #if url.endswith(".jpeg") or url.endswith(".jpg"):
    urlretrieve (url, "input.jpg")
    im = Image.open(r"input.jpg")
    img = prep(im)
    cv2.imwrite("input.png", img)
    
    image = cv2.imread("input.png")
    
    #getting image in the correct orientation
    try:
        angle=int(re.search('(?<=Orientation in degrees: )\d+', pytesseract.image_to_osd(image)).group(0))
        filename = "{}.png".format(os.getpid())
    
        cv2.imwrite(filename,ndimage.rotate(image, angle))
    
        #plt.imshow(ndimage.rotate(image, angle))
    
        text = pytesseract.image_to_string(Image.open(filename),config="-l eng --oem 1 --psm 3")
        text=f1(text)
        os.remove(filename)
        
        return text
    
    except TesseractError as e:
        c=str(e.message)
        text = pytesseract.image_to_string(Image.open("input.png"),config="-l eng --oem 1 --psm 3")
        text=f1(text)
        #os.remove(filename)
        print(c) 
        return text
        

    



def send(customer):
    cus_name = name_cus(customer)
    if cus_name!="":
        cus_name = cus_name.split('\n')[0].strip()
    
    ind=len(cus_name)
    if "designation" in cus_name.lower():
        ind=cus_name.lower().index("designation")
    elif "department" in cus_name.lower():
        ind=cus_name.lower().index("department")
    else:
        ind=len(cus_name)
    cus_name=cus_name[:ind]
        
    cus_name = re.sub("[^A-Za-z.  ]", "", cus_name).strip()

    bank = bank_name(customer)
    if bank!="":
        bank = bank.split('\n')[0].strip()
    if ":" in bank:
        bank=bank[bank.index(":"):]
    bank = re.sub("[^A-Za-z. , ]", "", bank).strip()
    
    
    acc = account_number(customer)
    acc = re.sub("[^0-9xX ]", "", acc).strip()
    if acc!="":
        acc = acc.split('   ')[0].strip()
    l=acc.split(" ")
    for x in l:
        if len(x)>=9:
            acc=x

    gross = gross_sal(customer)
    gross = re.sub("[^0-9./, ]", "", gross).strip()
    gl = gross.split(" ")
    gl = [x for x in gl if x != " " and x!="" and x!="," and x!="."]
    if gl!=[]:
        gross1=gl[0]
    else:
        gross1=""

    net = net_sal(customer)
    net = re.sub("[^0-9., ]", "", net).strip()
    nl = net.split(" ")
    nl = [x for x in nl if x != " " and x!="" and x!="," and x!="."]
    if nl!=[]:
        net1=nl[0]
    else:
        net1=""
            

    date=time(customer)
    date = re.sub("[^0-9A-Za-z-/\.:, ]", "", date).strip()

    company = company_name(customer)
    company = re.sub("[^0-9A-Za-z/\., ]", "", company).strip()

    return cus_name,bank,acc,gross1,net1,date,company







url=input('Please Enter url of salary slip: ')




#if 'url' not in request.args:
#    return "Error: No url provided. Please specify a url.--->/api/v1/resources/salslip?url=url"

req = Request(url)
try:
    res = urlopen(req)
    if valid_url_extension(url)==False:
        print( "Please enter a valid URL to a pdf or an image--> .jpg .jpeg .png .pdf" ) 

    else:
        if'.pdf' in url:
            urlretrieve (url, "input.pdf")

            customer = main("input.pdf")

            if customer!="" and customer!=[]:
                cus_name,bank,acc,gross1,net1,date,company=send(customer)
            

            else:
                customer = pdf_img("input.pdf")
                cus_name,bank,acc,gross1,net1,date,company=send(customer)

            
            

            d = {
            "Employee Name": cus_name,
            "Company Name":company,
            "Issue date":date,
            "Net Salary":net1,
            "Gross Salary":gross1,
            "Bank Account Number":acc,
            "Bank Name":bank
            
                }  

            
                #print(customer)
                #except:
                #print("Sorry file can't be open")
                #print(d)
            
        if'.jpg' in url or '.jpeg' in url or '.png' in url:

            customer = img(url)
            cus_name,bank,acc,gross1,net1,date,company=send(customer)

        

            d = {
            "Employee Name": cus_name,
            "Company Name":company,
            "Issue date":date,
            "Net Salary":net1,
            "Gross Salary":gross1,
            "Bank Account Number":acc,
            "Bank Name":bank
            
                }  
        #print(d)
        @app.route("/")
        def hello():
            return jsonify(d)


        if __name__ == '__main__':
            app.run(debug=True,use_reloader=False)




except HTTPError as e:
    a="The server couldn't fulfill the request. Error code: "+str(e.code)
    print(a)
except URLError as e:
    b='We failed to reach a server. Reason: '+str(e.reason)
    print(b)
except PDFPageCountError as e:
    b=str(zlib.error)
    print(b)


    







