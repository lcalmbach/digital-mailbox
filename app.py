import streamlit as st
from os.path import exists
import pandas as pd
from datetime import datetime
import s3fs

saved_files = []
s3_path = r's3://lc-opendata01/'
local_path = './data/'
log_file = './versand.csv'
fs = s3fs.S3FileSystem()

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

st.markdown("### Willkommen bei der digitalen Mailbox📬")
st.markdown("**Statistisches Amt des Kantons Basel-Stadt**")
log_df = pd.read_csv(log_file,sep=';')
surname= st.text_input("Name")
firstname = st.text_input("Vornamen")
comment = st.text_area("Kommentar", help="Hier können sie bei Bedarf Bemerkungen zu ihrem Dateiversand deponieren")
uploaded_files = st.file_uploader(f"Ziehen sie bitte ihre Dateien in die Upload-Fläche", accept_multiple_files=True, type=['xlsx'])
#s3 = s3fs.S3FileSystem(anon=False)

if uploaded_files and firstname and surname:
    if st.button("Dateien senden"):
        for file in uploaded_files:
            filename = get_filename(file.name)
            with open(local_path + filename, 'wb') as f: 
                f.write(file.read()) 
            log_df.loc[len(log_df.index)] = [filename, firstname, surname, comment, datetime.now()]
            s3_filename = f"{s3_path}{filename}"
            fs.upload(local_path + filename, s3_path + filename)
            #    f.write(file.read()) 
            saved_files.append(filename)
        log_df.to_csv(log_file,sep=';',index=False)
        st.success('Vielen Dank! Die Datei wurde erfolgreich gespeichert')

        fs = s3fs.S3FileSystem()

    