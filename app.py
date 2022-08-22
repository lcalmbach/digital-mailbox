import streamlit as st
from os.path import exists
import pandas as pd
from datetime import datetime
import s3fs

version_date = '2022-08-21'
__version__ = '0.0.3'
__author_email__ = 'lcalmbach@gmail.com'
__author__ = 'Lukas Calmbach'
git_repo = 'https://github.com/lcalmbach/digitial-mailbox'
saved_files = []
s3_path = r's3://lc-opendata01/'
local_path = './data/'
log_file_remote = 'https://lc-opendata01.s3.amazonaws.com/versand.csv'
log_file_local = 'versand.csv'
fs = s3fs.S3FileSystem()

APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({version_date})<br>
    <a href="{git_repo}">git-repo</a>
    """

def get_filename(filename:str):
    fn = filename
    files_exists = exists(local_path + fn)
    version = 0
    while (files_exists):
        version +=1
        postfix = f"_{version}.xlsx"
        fn = fn = file.name.replace('.xlsx', postfix)
        files_exists = exists(local_path + fn)
    return fn


st.set_page_config(page_title='your_title', page_icon = '📬', layout = 'wide')
st.markdown("### Willkommen bei der digitalen Mailbox📬")
st.markdown("**Statistisches Amt des Kantons Basel-Stadt**")
log_df = pd.read_csv(log_file_remote, sep=';')
st.write(log_df)
surname= st.text_input("Name")
firstname = st.text_input("Vornamen")
comment = st.text_area("Kommentar", help="Hier können sie bei Bedarf Bemerkungen zu ihrem Dateiversand deponieren")
uploaded_files = st.file_uploader(f"Ziehen sie bitte ihre Dateien in die Upload-Fläche", accept_multiple_files=True, type=['xlsx'])

if uploaded_files and firstname and surname:
    if st.button("Dateien senden"):
        for file in uploaded_files:
            filename = get_filename(file.name)
            with open(local_path + filename, 'wb') as f: 
                f.write(file.read()) 
            log_df.loc[len(log_df.index)] = [filename, firstname, surname, comment, datetime.now()]
            fs.upload(local_path + filename, s3_path + filename)
            saved_files.append(filename)
        log_df.to_csv(log_file_local,sep=';',index=False)
        fs.upload(log_file_local, s3_path + log_file_local)
        st.success('Vielen Dank! Die Datei wurde erfolgreich gespeichert')

cols = st.columns([1,5])
with cols[0]:
    st.markdown('')
    st.markdown(APP_INFO, unsafe_allow_html=True)