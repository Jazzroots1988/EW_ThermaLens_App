import cv2
import numpy as np
import imutils
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
    temperature = random.randint(25, 55)

    for index, values in conteo_zonas.items():
        if values['cantidad_cuadros'] > 0:
            date, time = values['ultima_deteccion_puntos'].split(' ')
            ew_values = [str(index), str(opc_position), str(values['cantidad_puntos']), str(values['cantidad_cuadros']),
                         str(values['posicion_cuadros']), str(temperature), date, time, str(cell)]

            # sql loop configurations
            ew_cursor = instance_sql.cursor()
            sql_instruction = ('INSERT INTO EW_points_test_rev1 (indice, zona, cantid_puntos_enc, cantid_cuadros_enc,'
                               ' puntos_encont, temperatura_max, ult_detect_date, ult_detect_time, celda) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)')

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
    puntos_revisados = {}

    # connection string for database communication
    ew_db = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};' + r'SERVER=DESKTOP-EVG8NJP;'
                                                                          r'DATABASE=EW_testing'
                                                                          r';Trusted_Connection=yes;')
    flag = 0
    opc_count = 0
    opc_value = 0
    export_count = 0

    print("Running!")

    try:
        while True:

            # reshape image as the same from the beginning
            thermal_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_thermal.buf)
            normal_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_normal.buf)#654
            draw_image = np.ndarray((480, 654, 3), dtype=np.uint8, buffer=shared_draw.buf)

            if thermal_image is None:
                break

            # search hot points
            heat_points = heat_seeker(thermal_image)

            # make the frame with thresholds
            frame_boundaries = draw_image


            if opc_count % 100 == 0:
                # read the crane position
                opc_value = int(opc_read.data_extract())
                opc_count = 0

            opc_count += 1

            if opc_value in [20, 40, 50]:

                conteo = {zona: {'cantidad_puntos': 0, 'cantidad_cuadros': 0, 'ultima_deteccion_puntos': None,
                                 'ultima_deteccion_cuadros': None, 'posicion_cuadros': []} for zona in zonas}
                puntos_revisados = {}

                # control for exporting action below
                export_opc = opc_value
                opc_value = 0

                for box in heat_points[1]:

                    (x, y, w, h) = box
                    cv2.rectangle(frame_boundaries, (x, y), (x + w, y + h), (255, 255, 0), 3)
                    cv2.circle(frame_boundaries, (int(x + w / 2), int(y + h / 2)), 4, (0, 0, 255), -1)

                    # Verificar en qué zona se encuentra el punto (x, y)
                    for zona, limites in zonas.items():
                        #print(zona)
                        #print(int(x + w/2), int(y + h/2))
                        if limites[0][0] <= int(x + w/2) < limites[0][1] and limites[1][0] <= int(y + h/2) < limites[1][1]:

                            # Verificar si el punto ha sido revisado anteriormente
                            if (x, y) not in puntos_revisados:
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                print(f'Punto en Zona: {zona}, Fecha y Hora: {current_time}')
                                puntos_revisados[(x, y)] = (zona, current_time)

                                # Actualizar el diccionario conteo con la hora y fecha de detección de puntos
                                conteo[zona]['cantidad_puntos'] += 1
                                conteo[zona]['ultima_deteccion_puntos'] = current_time

                            # Verificar si el cuadro ha sido revisado anteriormente
                            if (x, y, w, h) not in puntos_revisados:
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                print(f'Cuadro en Zona: {zona}, Fecha y Hora: {current_time}')
                                puntos_revisados[(x, y, w, h)] = (zona, current_time)

                                # Actualizar el diccionario conteo con la hora y fecha de detección de cuadros
                                conteo[zona]['cantidad_cuadros'] += 1
                                conteo[zona]['ultima_deteccion_cuadros'] = current_time

                                # Agregar la posición del cuadro en la lista de posiciones dentro del diccionario
                                conteo[zona]['posicion_cuadros'].append((x, y, w, h))

                            break

                # here writes to sql instance
                zone_count(conteo, ew_db, opc_position=export_opc)

                del conteo
                del puntos_revisados
                #frame_final = np.concatenate((normal_image, frame_boundaries), axis=1)
                #frame_final = imutils.resize(frame_final, width=1200)
                #cv2.imshow("Image", frame_final)
                # cv2.imshow("mask", mask)



                # if "q" key is pressed finish the program
                #if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break

            else:

                for contour, box in zip(heat_points[0], heat_points[1]):

                    (x, y, w, h) = box
                    cv2.rectangle(frame_boundaries, (x, y), (x + w, y + h), (255, 255, 0), 3)
                    cv2.circle(frame_boundaries, (int(x + w / 2), int(y + h / 2)), 4, (0, 0, 255), -1)

                #frame_final = np.concatenate((normal_image, frame_boundaries), axis=1)
                #frame_final = imutils.resize(frame_final, width=1200)
                #cv2.imshow("Image", frame_final)
                # cv2.imshow("mask", mask)

                # if "q" key is pressed finish the program
                    '''if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    
            cv2.destroyAllWindows()'''

    finally:

        # Cerrar y eliminar la memoria compartida al finalizar
        if shared_thermal is not None:
            shared_thermal.close()
            shared_thermal.unlink()

        if shared_normal is not None:
            shared_normal.close()
            shared_normal.unlink()

        if shared_draw is not None:
            shared_draw.close()
            shared_draw.unlink()

        print("shared memory closed")
