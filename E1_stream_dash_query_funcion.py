import pyodbc
import cv2
import numpy as np
from multiprocessing import shared_memory
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

height, width = 480, 654
image_detections = shared_memory.SharedMemory(create=True, name="ImageAnnotations", size=width * height * 3)
buffer_data = shared_memory.SharedMemory(create=True, name="bufferData", size=4*100)

def visualization_lines(frame):

    frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

    # draw a rectangle over the screen to separate left and right places
    frame_coordinates = frame.shape[:2]
    cv2.rectangle(frame, (10, 10), (frame_coordinates[1] - 10, frame_coordinates[0] - 10), (0, 255, 0), thickness=2)

    # draw a line in the middle, to separate left and right sides
    cv2.line(frame, (int((frame_coordinates[1]) / 2) - 45, int((10 + 10) / 2)),
             (int((10 + frame_coordinates[1] - 10) / 2) - 45,
              int((frame_coordinates[0] - 10 + frame_coordinates[0] - 10) / 2))
             , (0, 255, 0), thickness=2)

    # Draw 24 horizontal lines across the image
    for line in range(10):
        position = 10 + line * 50  # Calculate the position based on the line number

        # Draw a line across the screen
        cv2.line(frame, (10, int(position)), (frame_coordinates[1] - 10, 25 + int(position)), (0, 0, 255), thickness=3)

    return frame

def dash_query(date_ini, date_end, cell, time_ini, time_end, width=width, height=height):

    shared_image_annot = np.ndarray((height, width, 3), dtype=np.uint8, buffer=image_detections.buf)

    ew_db = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};' + r'SERVER=localhost\SQLEXPRESS;'
                                                                          r'DATABASE=EW_testing'
                                                                          r';Trusted_Connection=yes;')
    ew_cursor = ew_db.cursor()
    date_ini = date_ini#str(input("fecha inicial "))
    date_end = date_end#str(input("fecha final "))
    cell = str(cell)
    time_ini = time_ini.strftime('%H:%M:%S')
    time_end = time_end.strftime('%H:%M:%S')

    # Consulta a la base de datos con query parametrizado
    #sql_query = "SELECT puntos_encont, zona, cantid_puntos_enc FROM EW_points_test_rev2 WHERE ult_detect_date BETWEEN ? AND ?"
    sql_query = ("select puntos_encont, zona, cantid_puntos_enc, temperatura_max, indice from EW_points_test_rev1"
                 " where celda = ? and ult_detect_date BETWEEN ? and ? and ult_detect_time between ? and ?")
    ew_cursor.execute(sql_query, (cell, date_ini, date_end, time_ini, time_end))
    query = ew_cursor.fetchall()

    # Procesamiento de la consulta
    q_tuples = [(eval(q[0]), q[1], q[2], q[3]) for q in query]
    n_rows = len(q_tuples)
    boxes = [None] * n_rows
    zona = [None] * n_rows
    cant_points = [None] * n_rows
    temperature = [None] * n_rows
    for i, tup in enumerate(q_tuples):
        boxes[i] = tup[0]
        zona[i] = tup[1]
        cant_points[i] = tup[2]
        temperature[i] = tup[3]

    # Dibujar círculos en lienzo
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    canvas = visualization_lines(canvas)

    for box in boxes:
        for circle in box:
            x, y, w, h = circle
            color = np.random.randint(0, 255, size=3).tolist()  # escoge un color aleatorio
            center = (x + int(w/2), y + int(h/2))  # centro del círculo
            cv2.circle(canvas, center, min(w, h)//2, color, thickness=-1)

    shared_image_annot[:] = canvas[:]
    return None

def heat_map_EW(cell):

    ew_db = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};' + r'SERVER=localhost\SQLEXPRESS;'
                                                                        r'DATABASE=EW_testing'
                                                                        r';Trusted_Connection=yes;')
    ew_cursor = ew_db.cursor()
    cell = str(cell)

    # Consulta a la base de datos con query parametrizado
    sql_query = "select cantid_puntos_enc, indice, temperatura_max, ult_detect_date, ult_detect_time from EW_points_test_rev2 where celda = ?"
    ew_cursor.execute(sql_query, (cell))
    query = ew_cursor.fetchall()

    data = [(int(q[0]), eval(q[1]), q[2], dt.datetime.combine(q[3], q[4]))for q in query]#.strftime("%Y-%m-%d").strftime("%H:%M")

    data = pd.DataFrame(data, columns=['cant_puntos', 'lugar_mapa', 'temp_max', 'complete_datetime'])
    place = 2
    #data['Date_datetime'] = pd.to_datetime(data.complete_datetime, format="%m/%d/%Y %H:%M")
    data['day'] = data.complete_datetime.dt.day
    data['hour'] = data.complete_datetime.dt.hour
    data['weekday'] = data['complete_datetime'].apply(lambda x: x.strftime('%w'))


    group_data = data.groupby(['day', 'hour', 'cant_puntos'])['lugar_mapa'].unique().reset_index()
    group_data_1 = data.groupby(['day', 'hour', 'lugar_mapa'])['cant_puntos'].apply(list).reset_index()
    group_data_1['cant_puntos'] = group_data_1['cant_puntos'].apply(lambda x: sum(x))
    #group_data_1 = group_data_1.drop(columns=['lugar_mapa'])

    group_data_x = group_data_1.pivot(index='day', columns='hour', values='cant_puntos').fillna(0)

    plt.figure(figsize=(12,6))
    sns.heatmap(group_data, cmap="YlGnBu", annot=True, fmt=".0f")
    plt.title(f'Heat points frequency {cell}')
    plt.xlabel("Hour")
    plt.ylabel("Day")
    plt.show()



    place = 2

def buffer_dataRT():
    last_data = np.ndarray((1,100), dtype=np.float32, buffer=buffer_data.buf)

    ew_db = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};' + r'SERVER=localhost\SQLEXPRESS;'
                                                                        r'DATABASE=EW_testing'
                                                                        r';Trusted_Connection=yes;')
    ew_cursor = ew_db.cursor()

    sql_query = "SELECT TOP  5 indice, cantid_puntos_enc, temperatura_max, celda, ult_detect_date, ult_detect_time from EW_points_test_rev1 order by id desc"
    ew_cursor.execute(sql_query)
    query = ew_cursor.fetchall()
    data = [(q[0], q[1], q[2], q[3], q[4], q[5]) for q in query]
    df = pd.DataFrame(data, columns=['indice', 'cantidad_puntos', 'temp_max', 'celda', 'ult_fecha', 'ult_tiempo']).reset_index(drop=True)

    return df


