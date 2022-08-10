import streamlit as st
from os.path import exists

saved_files = []

def get_filename(filename:str):
    fn = f'./data/{filename}'  
    files_exists = exists(fn)
    version = 0
    while (files_exists):
        version +=1
        postfix = f"_{version}.xlsx"
        fn = fn = f"./data/{file.name.replace('xlsx',postfix)}"  
        files_exists = exists(fn)
    return fn

st.markdown("### Willkommen bei der digitalen Mailbox")
st.markdown("**Statistisches Amt des Kantons Basel-Stadt**")
surname= st.text_input("Name")
firstname = st.text_input("Vornamen")
uploaded_files = st.file_uploader(f"Ziehen sie bitte ihre Dateien in die Upload-Fläche", accept_multiple_files=True, type=['xlsx'])
if uploaded_files:
    if st.button("Dateien senden"):
        for file in uploaded_files:
            filename = get_filename(file.name)
            with open(filename, 'wb') as f: 
                f.write(file.read()) 
            saved_files.append(filename)
        st.write("Folgende Dateien wurden gespeichert:")
        
        for filename in saved_files:
            st.write(filename)