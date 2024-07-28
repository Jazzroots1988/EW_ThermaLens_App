import streamlit as st
from multiprocessing import shared_memory
import numpy as np
import cv2
import imutils
import time
from stream_dash_query_funcion import buffer_dataRT

st.title("Real Time Visual")
webpage_dist = st.empty()

shared_thermal = shared_memory.SharedMemory(name="SharedThermal")
shared_normal = shared_memory.SharedMemory(name="SharedNormal")
buffer_data = shared_memory.SharedMemory(name="bufferData")

try:
	while True:

		dataframe4streamlit = buffer_dataRT()

		# reshape image as the same from the beginning
		thermal_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_thermal.buf)
		normal_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_normal.buf)
		frame_final = np.concatenate((normal_image, thermal_image), axis=1)
		frame_final = cv2.cvtColor(frame_final, cv2.COLOR_BGR2RGB)
		frame_final = imutils.resize(frame_final, width=2500)

		with webpage_dist.container():
			image_disp = st.columns(1)

			with image_disp[0]:
				st.write("Visual Now")
				st.image(frame_final)
				st.dataframe(dataframe4streamlit)
	
		time.sleep(0.1)
	
except KeyboardInterrupt:
	shared_thermal.close()
	shared_thermal.unlink()
	shared_normal.close()
	shared_normal.unlink()


