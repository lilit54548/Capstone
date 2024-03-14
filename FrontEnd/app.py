# File: app.py
import streamlit as st

st.title('Fast UI with Streamlit')

# create some UI elements
st.write("Hello, this is a simple Fast UI using Streamlit in Docker.")

# interaction: button click
if st.button('Say hello'):
    st.write('Why hello there')
else:
    st.write('Goodbye')

# run this with `streamlit run app.py`
