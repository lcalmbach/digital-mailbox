import streamlit as st
from os.path import exists
import pandas as pd
from datetime import datetime
import s3fs
import os

import tools
import mail_template

version_date = '2023-22-03'
__version__ = '0.0.5'
__author_email__ = 'lcalmbach@gmail.com'
__author__ = 'Lukas Calmbach'
git_repo = 'https://github.com/lcalmbach/digitial-mailbox'

saved_files = []
s3_bucket = 'lc-opendata01'
s3_path = r's3://lc-opendata01/'
local_path = './data/'
log_file_remote = 'https://lc-opendata01.s3.amazonaws.com/versand.csv'
log_file_local = 'versand.csv'

APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({version_date})<br>
    <a href="{git_repo}">git-repo</a>
    """
MAIL_LISTE_DATEI = './mail-liste.csv'
CODE_LEN = 20

def get_filename(filename:str):
    fn = filename
    files_exists = exists(local_path + fn)
    version = 0
    while (files_exists):
        version +=1
        postfix = f"_{version}.xlsx"
        fn = fn = filename.replace('.xlsx', postfix)
        files_exists = exists(local_path + fn)
    return fn

def get_fs():
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    fs = s3fs.S3FileSystem(anon=False, key=access_key, secret=secret_key)
    return fs

def init_mail_verteiler():
    df = pd.read_csv(MAIL_LISTE_DATEI, sep=';')
    for index,row in df.iterrows():
        df['code'] = tools.randomword(CODE_LEN)
    df.to_csv('./mail-liste.csv', index=False, sep=';')

def send_invitation():
    pass

def send_confirmation_mail(record: dict, filename):
    # Define email parameters
    email = {}
    email['password'] = tools.get_config_value('MAIL_PASSWORD')
    email['sender_email'] = "lukascalmbachapps@gmail.com"
    email['receiver_email'] = record['email']
    email['subject'] = mail_template.bestaetigung_betreff
    email['body'] = mail_template.bestaetigung_text.format(record, filename)
    tools.send_mail(email)

def verify_code(code):
    df = pd.read_csv(MAIL_LISTE_DATEI, sep = ';')
    df = df[df['code'] == code]
    if len(df) > 0:
        return dict(df.iloc[0])
    else:
        st.warning("Dieser Code ist nicht korrekt, bitte copy/pasten sie den Code aus der Mail-Einladung des Statistischen Amts oder kontaktieren sie stata@bs.ch für einen neuen Code.")
        return False

def main():
    st.set_page_config(page_title='digiMail', page_icon = '📬', layout = 'wide')
    fs = get_fs()
    st.markdown("### Willkommen bei der digitalen Mailbox📬")
    st.markdown("**Statistisches Amt des Kantons Basel-Stadt**")
    log_df = pd.read_csv(log_file_remote, sep=';')
    code= st.text_input(f"{CODE_LEN}-stelliger alphanumerischer Code (bitte aus Einladungsmail copy/pasten)")
    sender = verify_code(code)
    if sender:
        st.info(f"Willkommen {sender['vorname']}! Du kannst bei Bedarf einen Kommentar erfassen und anschliessend deine Datei in das Datei-Upload Feld ziehen.")
        comment = st.text_area("Kommentar", help="Hier können sie bei Bedarf Bemerkungen zu ihrem Dateiversand deponieren")
        uploaded_files = st.file_uploader(f"Ziehen sie bitte ihre Dateien in die Upload-Fläche", accept_multiple_files=True, type=['xlsx'])

        if st.button("Datei senden"):
            for file in uploaded_files:
                filename = get_filename(file.name)
                with open(local_path + filename, 'wb') as f: 
                    f.write(file.read()) 
                log_df.loc[len(log_df.index)] = [filename, sender['vorname'], sender['vorname'], comment, datetime.now(), 'ungelesen', None, None]
                fs.upload(local_path + filename, s3_path + filename)
                saved_files.append(filename)
            log_df.to_csv(log_file_local,sep=';',index=False)
            fs.upload(log_file_local, s3_path + log_file_local)
            st.success('Vielen Dank! Die Datei wurde erfolgreich gespeichert')
            send_confirmation_mail(sender, filename)

    cols = st.columns([1,4])
    with cols[0]:
        st.markdown('')
        st.markdown(APP_INFO, unsafe_allow_html=True)

if __name__ == '__main__':
    main()