import streamlit as st
from multiprocessing import shared_memory
import numpy as np
import cv2
import imutils
import time
from stream_dash_query_funcion import buffer_dataRT
import json
from streamlit_lottie import st_lottie

st.markdown('<p class="title">Real Time View</p>', unsafe_allow_html=True)

webpage_dist = st.empty()
#Invoke sharedmemory
shared_thermal = shared_memory.SharedMemory(name="SharedThermal")
shared_normal = shared_memory.SharedMemory(name="SharedNormal")



while True:
	dataframe4streamlit,temp_max = buffer_dataRT()
	# reshape image as the same from the beginning
	thermal_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_thermal.buf)
	normal_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_normal.buf)

	
	frame_final = np.concatenate((normal_image, thermal_image), axis=1)
	frame_final = cv2.cvtColor(frame_final, cv2.COLOR_BGR2RGB)
	frame_final = imutils.resize(frame_final, width=2500)

	with webpage_dist.container():
		st.image(frame_final)
		st.write("")
		column_order = st.columns(2)
		with column_order[0]:
			st.markdown('<p class="subtitle3">Last detections</p>', unsafe_allow_html=True)
			st.dataframe(dataframe4streamlit,hide_index=True)
		with column_order[1]:	
			st.markdown('<p class="subtitle3">Max Temperature Registered</p>', unsafe_allow_html=True)
			st.dataframe(temp_max, hide_index=True)

	time.sleep(0.1)








