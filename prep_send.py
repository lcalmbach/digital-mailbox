import boto3
import pandas as pd
import requests
import json
from datetime import datetime
import smtplib
import socket
import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


BUCKET_NAME = 'lc-opendata01'

cfg = configparser.ConfigParser()
cfg.read("config.cfg")


def send_mail(catalog, new_items):
    # Define email parameters
    new_items = [f"{catalog}/explore/dataset/{x}/" for x in new_items]
    sender_email = "lukascalmbachapps@gmail.com"

    hostname = socket.gethostname()
    if hostname.lower() == "liestal":
        password = cfg["default"]["MAIL_PASSWORD"]
    else:
        pass
        # password = st.secrets["APP_PASSWORD"]
    receiver_email = "lcalmbach@gmail.com"

    subject = "ODS-Explorer new dataset notification"
    body = f"""Hello!\nNew datasets have been discovered for catalog {catalog}:\n{'</br>'.join(new_items)}\n\n
If you wish to unsubscribe from this service, please navigate to https://lcalmbach-ogd-bs-browser-app-as449l.streamlit.app/ 
then select the subscribe option from the menu and unselect the subscribe checkbox.\n\nHave a nice day!\nods-browser@yourService"""

    # Create a MIME message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Connect to SMTP server and send email
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, password)
        smtp.send_message(message)


def get_s3_file(filename: str):
    from io import BytesIO

    session = boto3.Session()
    s3_client = session.client("s3")

    f = BytesIO()
    s3_client.download_fileobj(BUCKET_NAME, filename, f)
    data = json.loads(f.getvalue(), strict=False)
    return dict(data)


def compare_catalogs(catalog_dict):
    for catalog, item in catalog_dict.items():
        current_datasets = get_datasets(catalog)
        new_items = [x for x in current_datasets if x not in item["datasets"]]
        if len(new_items) > 0:
            catalog_dict[catalog] = {
                "datasets": current_datasets,
                "timestamp": datetime.now().strftime("%Y-%m-%d H:M"),
            }
            send_mail(catalog, new_items)
    put_s3_file(catalog_dict)


def put_s3_file(catalog_dict: dict):
    s3 = boto3.resource("s3")
    object = s3.Object(BUCKET_NAME, CATALOG_FILE)
    object.put(Body=json.dumps(catalog_dict))


def main():
    data = get_s3_file(CATALOG_FILE)
    compare_catalogs(data)


if __name__ == "__main__":
    main()
