import streamlit as st
import pyodbc
from PIL import Image



st.markdown('<p class="title">Detection Data</p>', unsafe_allow_html=True)
st.markdown('<p class="paragraph">Select a filter to get the image with the detection and see the temperature</p>', unsafe_allow_html=True)
st.write("")


# connection string
conn_string = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};' + r'SERVER=DESKTOP-EVG8NJP;'
                                                                          r'DATABASE=EW_testing'
                                                                          r';Trusted_Connection=yes;')

# Columns and sql cursor setting
list_columns = ['ult_detect_date', 'ult_detect_time', 'celda', 'zona']
query_results = []
db_cursor = conn_string.cursor()

# query and data retrieval
for comm in list_columns:
    command_sql = f'select distinct {comm} from EW_points_test;'
    db_cursor.execute(command_sql)
    result = db_cursor.fetchall()
    result = [str(element[0]) for element in result]
    query_results.append(result)


column_time_date_cell = st.columns(4)
with column_time_date_cell[0]:
    option_date_ini = st.selectbox("Filter by date", (query_results[0]))
with column_time_date_cell[1]:
    option_date_end = st.selectbox("Filter by Time", (query_results[1]))
with column_time_date_cell[2]:
    option_date_end = st.selectbox("Filter by cell", (query_results[2]))
with column_time_date_cell[3]:
    option_date_end = st.selectbox("Filter by zone", (query_results[3]))


# column_image = st.columns(3)
# with column_image[1]:
st.write("")
image = Image.open('G:/Mi unidad/Streamlit//image_test_reg/Detection_2024-07-16 16_17_37.png')
st.image(image, caption='Detection_2024-07-09 12_13_46', width=800)
    
