import streamlit as strl

def clean_image():
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    strl.markdown(hide_streamlit_style, unsafe_allow_html=True) 