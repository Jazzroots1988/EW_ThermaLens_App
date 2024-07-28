import streamlit as st
from streamlit_lottie import st_lottie
import json
import os

with open("assets\Animation5_intro.json", "r") as f:
    data = json.load(f)

col =st.columns(3)
with col[0]:
    st.markdown('<p class="title">Welcome</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">EW - Seeker</p>', unsafe_allow_html=True)
    st.markdown('<p class="paragraph">Image processing for a thermal camera and data analysis</p>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<p class="paragraph">Testing Version</p>', unsafe_allow_html=True)
    st.markdown('<p class="paragraph">Last update : 11 julio 2024</p>', unsafe_allow_html=True)
    st.markdown('<p class="paragraph">Version 1.01</p>', unsafe_allow_html=True)

with col[1]:
    st_lottie(data, key="welcome_animation2",height=300, width=350, quality="high", reverse=True)

with col[2]:
    st.markdown('<p class="subtitle3"> Start Services</p>', unsafe_allow_html=True)
    bp_on = st.button("ON Services")
    bp_off = st.button("OFF Services")
try:
    
    if bp_off ==True:
        os.system("backgroundProcess_Off.bat")
        st.session_state["server_state"] = bp_off
    if bp_on:
        os.system("backgroundProcess_On.bat")
        st.session_state["server_state"] = bp_on
except SystemExit: 
    os.system("backgroudProcess_Off.bat")

