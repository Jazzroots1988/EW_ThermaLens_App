import streamlit as st
import pyodbc
from stream_dash_query_funcion import dash_query
from multiprocessing import shared_memory
import numpy as np
import datetime
st.markdown('<p class="title">Data Analysis</p>', unsafe_allow_html=True)

# connection string
conn_string = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};' + r'SERVER=localhost\SQLEXPRESS;'
                                                                          r'DATABASE=EW_testing'
                                                                          r';Trusted_Connection=yes;')



# Columns and sql cursor setting
list_columns = ['celda', 'zona']
query_results = []
db_cursor = conn_string.cursor()

# query and data retrieval
for comm in list_columns:
    command_sql = f'select distinct {comm} from EW_points_test_rev3;'
    db_cursor.execute(command_sql)
    result = db_cursor.fetchall()
    result = [str(element[0]) for element in result]
    query_results.append(result)

today = datetime.datetime.now()
jan_1 = datetime.date(today.year -1, 1, 1)
dec_31 = datetime.date(today.year + 1, 12, 31)

option_date = st.date_input(
    "Select a range of data",
    (today, datetime.date(today.year,today.month, today.day+3)),
    jan_1,
    dec_31,
    format="DD.MM.YYYY",
)
option_date_ini = option_date[0]
option_date_end = option_date[0]

placing_widgets = st.empty()

# dashboard distribution by two columns
with placing_widgets.container():
    column_hours_zone =st.columns(4)
    with column_hours_zone[0]:
        option_time_ini = st.time_input('Initial Hour', datetime.time(0, 0))
    with column_hours_zone[1]:
        option_time_end = st.time_input('Final Hour', datetime.time(23, 59))
    with column_hours_zone[2]:
        zone = st.selectbox("Zone Number", (query_results[1]))
    with column_hours_zone[3]:
        cell = st.selectbox("Cell Number", (query_results[0]))

dash_query(option_date_ini, option_date_end, cell, option_time_ini, option_time_end)
#heat_map_EW(cell)
shared_annotation = shared_memory.SharedMemory(name="ImageAnnotations")
annotation_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_annotation.buf)
st.write("")
col =st.columns(2)

with col[1]:
    st.image(annotation_image)
