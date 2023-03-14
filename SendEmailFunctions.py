import numpy as np
import smtplib, ssl
from email.message import EmailMessage
import json


def send_start_mail(receiver_email, name_applicant, email_info_file_path = "email_info.json") :
    port = 465  # For SSL
    with open(email_info_file_path, 'r') as fp:
        email_info = json.load(fp)

    email = email_info["ADDRESS"]
    password = email_info["PASSWORD"]

    receiver_email

    em = EmailMessage()
    em['From'] = email
    em['To'] = receiver_email
    em['Subject'] = "QCM - " + name_applicant
    em.set_content(name_applicant + " has started his QCM.")

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)
        server.sendmail(email, receiver_email, em.as_string())

def create_message_from_dictionary(dictionary, name) :
    head_message = '     ~~~~ Résultats de ' + name + ' ~~~~ \n'
    nb_questions = len(dictionary)
    score = 0

    body_message = ''

    keys = list(dictionary.keys())
    keys.sort()
    i=0

    for key in keys:
        i+=1
        body_message += "    ~~ QUESTION " + str(i) + "/" + str(nb_questions) + " " 
        body_message += dictionary[key]["Question"] 
        body_message += "\nSUBMITTED ANSWER : " + str(dictionary[key]["Submitted answer"])
        body_message += "\n\n\n"
    
    head_message += "     ~~~~ "



    return head_message + body_message

def send_results_by_mail(receiver_email, name_applicant, dictionary_to_send, email_info_file_path = "email_info.json") :

    port = 465  # For SSL
    with open(email_info_file_path, 'r') as fp:
        email_info = json.load(fp)

    email = email_info["ADDRESS"]
    password = email_info["PASSWORD"]

    receiver_email

    em = EmailMessage()
    em['From'] = email
    em['To'] = receiver_email
    em['Subject'] = "QCM - " + name_applicant + " - Results"
    em.set_content(create_message_from_dictionary(dictionary_to_send, name_applicant))

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email, password)
        server.sendmail(email, receiver_email, em.as_string())