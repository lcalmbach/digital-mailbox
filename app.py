import streamlit as st
from io import StringIO

st.markdown("## Digitaler Briefkasten")
uploaded_files = st.file_uploader("Ziehe deine Dateien in die untenstehende grahe Fläche",accept_multiple_files=True, type=['xlsx', 'csv'])
if uploaded_files:
    if st.button('Send files'):
        for file in uploaded_files:
            bytes_data = file.getvalue()
            with open(file.name, "wb") as f:
                f.write(bytes_data)