
from pathlib import Path
import streamlit as st
import os
st.set_page_config(layout='wide')

# Path Settings for CSS
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd() #Enconrtar el Current working directory cwd
css_file = current_dir /"styles" / "main.css"

# Load CSS file
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html =True)
#_________________________________________________________________________________________________________________________________________
#Config Markdown for title size
st.markdown("<style>.title {font-size:50px !important;}</style>", unsafe_allow_html=True)
#Config Markdown for subtitle size
st.markdown("<style>.subtitle {font-size:32px !important;}</style>", unsafe_allow_html=True)
#Config Markdown for subtitle2 size
st.markdown("<style>.subtitle2 {font-size:25px !important;}</style>", unsafe_allow_html=True)
#Config Markdown for subtitle3 size
st.markdown("<style>.subtitle3 {font-size:25px !important;}</style>", unsafe_allow_html=True)
#Config Markdown for paragraph size
st.markdown("<style>.paragraph {font-size:16px !important;}</style>", unsafe_allow_html=True)

#_________________________________________________________________________________________________________________________________________
#Pages (.py) order and information for sidebar
homepage_dash  = st.Page(
    page="homepage.py",
    title="Homepage",
    icon=":material/location_city:",
    default=True,
)
realtime_dash  = st.Page(
    page="realtime_dash.py",
    title="Real Time View",
    icon=":material/nest_cam_iq:",
)

image_detections_dash  = st.Page(
    page="detection_dash.py",
    title="Detections",
    icon=":material/detection_and_zone:",
)

data_analisys_dash  = st.Page(
    page="data_analysis_dash.py",
    title="Data Analysis",
    icon=":material/monitoring:",
)

operator_dash  = st.Page(
    page="operator_dash.py",
    title="Operator View",
    icon=":material/camera_video:",
)

testing2  = st.Page(
    page="testing2.py",
    title="Predictions",
    icon=":material/sweep:",
)



#Display logo in sidebar
st.logo("assets/LogoTHTech.png")
#Display pages in sidebar
pg= st.navigation(pages=[homepage_dash, realtime_dash, image_detections_dash, data_analisys_dash, operator_dash, testing2])
#Footer Sidebar
st.sidebar.markdown("Designed and builded in 2024")

pg.run()


# https://www.youtube.com/watch?v=obYhL4V1-lE


