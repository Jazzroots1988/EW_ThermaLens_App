import cv2
import numpy as np
#from streaming_video import videoStreaming
import imutils
import time
from datetime import datetime
from client_opc_simple import OpcRead
import pyodbc
from multiprocessing import shared_memory
import random

# function to sort the contours (from left to right only! and top to bottom too!)
def sort_contours(contours):
    if len(contours) < 2:
        contours = []
        boundingBoxes = []

    else:
        #  make a list of bounding boxes and sort them from top to bottom
        boundingBoxes = [cv2.boundingRect(c) for c in contours]
        (contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes),
                                                key=lambda b: b[1][0], reverse=False))
    return contours, boundingBoxes

def get_contours(frame_analysed):
    cnts = cv2.findContours(frame_analysed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # Filtrar contornos en función de su área
    cnts = [cnt for cnt in cnts if cv2.contourArea(cnt) > 150]

    cnts = sorted(cnts, key=cv2.contourArea, reverse=False)[:5]

    return cnts

def heat_seeker(frame):
    # transform BGR color space to HSV
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(frame, colorRange[0], colorRange[1])
    mask = cv2.erode(mask, erode_kernel, iterations=2)
    mask = cv2.dilate(mask, dilate_kernel, iterations=4)

    # getting the contours and sort them
    cnts = get_contours(mask)
    heat_points = sort_contours(cnts)

    return heat_points


def zone_count(conteo_zonas, instance_sql, opc_position):

    ew_values = []

    cell = random.randint(1, 20)
    temperature = random.randint(20, 50)

    for index, values in conteo_zonas.items():
        if len(values['box_position']) > 0:
            date, time = values['last_detection'].split(' ')
            ew_values = [str(index), str(opc_position), str(values['points']), str(tuple(values['box_position'])), str(temperature), date, time, str(cell)]
            print(ew_values)

            # sql loop configurations
            ew_cursor = instance_sql.cursor()
            sql_instruction = 'INSERT INTO EW_points_test_rev3 (indice, zona, cantid_puntos_enc, puntos_encont, temperatura_max, ult_detect_date, ult_detect_time, celda) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'

            # writer instance for sql
            ew_cursor.execute(sql_instruction, ew_values)
            ew_cursor.commit()



            print(f'Los datos se han guardado correctamente en el archivo sql')


if __name__ == '__main__':



    # simplifies the opc connection
    opc_read = OpcRead(url='opc.tcp://127.0.0.1:1234')

    shared_thermal = shared_memory.SharedMemory(name="SharedThermal")
    shared_normal = shared_memory.SharedMemory(name="SharedNormal")
    shared_draw = shared_memory.SharedMemory(name="SharedDraw")

    # see the color ranges for high temperature color
    colorRange = [(129, 0, 144), (161, 142, 255)]

    # make the kernels to dilate and erode process
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    erode_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    # Definir las zonas y sus límites
    zonas = {
        (1, 1): ((8, 281), (8, 60)),
        (1, 2): ((8, 281), (62, 110)),
        (1, 3): ((8, 281), (111, 158)),
        (1, 4): ((8, 281), (159, 208)),
        (1, 5): ((8, 281), (209, 260)),
        (1, 6): ((8, 281), (261, 310)),
        (1, 7): ((8, 281), (311, 358)),
        (1, 8): ((8, 281), (359, 410)),
        (1, 9): ((8, 281), (411, 460)),
        (2, 1): ((282, 643), (35, 84)),
        (2, 2): ((282, 643), (85, 134)),
        (2, 3): ((282, 643), (135, 183)),
        (2, 4): ((282, 643), (184, 234)),
        (2, 5): ((282, 643), (235, 285)),
        (2, 6): ((282, 643), (286, 333)),
        (2, 7): ((282, 643), (334, 384)),
        (2, 8): ((282, 643), (385, 434)),
        (2, 9): ((282, 643), (435, 470)),
    }

    # Mantener un diccionario de puntos revisados y el conteo de puntos por zona
    #puntos_revisados = {}

    # connection string for database communication
    ew_db = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};' + r'SERVER=DESKTOP-EVG8NJP;'
                                                                          r'DATABASE=EW_testing'
                                                                          r';Trusted_Connection=yes;')
    flag = 0
    opc_count = 0
    opc_value = 0
    export_count = 0
    export_opc = 0

    print("Running!")


    n = 10
    initial_time = time.time()
    opc_position_memo = 0

    while True:

        # reshape image as the same from the beginning
        thermal_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_thermal.buf)
        normal_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_normal.buf)#654
        draw_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_draw.buf)

        if thermal_image is None:
            break

        # search hot points
        heat_points = heat_seeker(thermal_image)


        if opc_count % 100 == 0:
            # read the crane position
            opc_value = int(opc_read.data_extract())
            opc_count = 0

        opc_count += 1

        if opc_value in [20, 25,50]:

            if opc_value != export_opc:
                puntos_revisados = {'indice': set()}

            #opc_value = opc_position_memo

            conteo_zonas = {zona: {'points': 0, 'box_position': set(), 'last_detection': None} for zona in zonas}

            # control for exporting action below
            export_opc = opc_value
            opc_value = 0

            # due the image present on shared memory changes everytime, is mandatory make a copy for ensure drawing
            processing_frame = draw_image.copy()


            for box in heat_points[1]:

                (x, y, w, h) = box
                cv2.rectangle(processing_frame, (x, y), (x + w, y + h), (255, 50, 0), 5)
                cv2.circle(processing_frame, (int(x + w / 2), int(y + h / 2)), 7, (255, 0, 0), -1)

                print((x, y) not in puntos_revisados['indice'])

                if (x, y) not in puntos_revisados['indice']:

                    # Verificar en qué zona se encuentra el punto (x, y)
                    for zona, limites in zonas.items():
                        #print(zona)
                        #print(int(x + w/2), int(y + h/2))
                        if limites[0][0] <= x < limites[0][1] and limites[1][0] <= y < limites[1][1]:
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            conteo_zonas[zona]['points'] += 1
                            conteo_zonas[zona]['box_position'].add((x,y,w,h))
                            conteo_zonas[zona]['last_detection'] = current_time
                            puntos_revisados['indice'].add((x,y))
                            # frame registration
                            cv2.imwrite('image_test_reg/Detection_{}.png'.format(
                                datetime.now().strftime("%Y-%m-%d %H_%M_%S")), processing_frame)

                else:
                    pass
            if any(value['points'] != 0 for value in conteo_zonas.values()):
                # here writes to sql instance
                zone_count(conteo_zonas, ew_db, opc_position=export_opc)

            final_time = time.time()
            #print(time.ctime(final_time))
            print((final_time) - (initial_time))
            if final_time-initial_time > 300:
            #if len(puntos_revisados) > n :
                #del puntos_revisados
                #print("hola")
                initial_time = time.time()
                puntos_revisados = {'indice': set()}
                #break
            print(puntos_revisados['indice'])

            del conteo_zonas


        else:
            pass
