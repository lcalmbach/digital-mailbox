import streamlit as st
import random
import string
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

DEV_MACHINES = ['liestal']
CONFIG_FILE = "config.cfg"

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def send_mail(mail):
    message = MIMEMultipart()
    message["From"] = mail['sender_email']
    message["To"] = mail['receiver_email']
    message["Subject"] = mail['subject']
    message.attach(MIMEText(mail["body"], "plain"))

    # Connect to SMTP server and send email
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(mail['sender_email'], mail['password'])
        smtp.send_message(message)

def get_config_value(key: str) -> str:
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE)
    if socket.gethostname().lower() in DEV_MACHINES:
        return cfg['default'][key]
    else:
        return st.secrets[key]