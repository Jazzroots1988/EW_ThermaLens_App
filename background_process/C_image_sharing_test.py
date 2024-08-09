import cv2
import numpy as np
from multiprocessing import shared_memory


def visualization_lines(frame):

    frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

    # draw a rectangle over the screen to separate left and right places
    frame_coordinates = frame.shape[:2]
    cv2.rectangle(frame, (10, 10), (frame_coordinates[1] - 10, frame_coordinates[0] - 10), (0, 255, 0), thickness=2)

    # draw a line in the middle, to separate left and right sides
    cv2.line(frame, (int((frame_coordinates[1]) / 2) - 45, int((10 + 10) / 2)),
             (int((10 + frame_coordinates[1] - 10) / 2) - 45,
              int((frame_coordinates[0] - 10 + frame_coordinates[0] - 10) / 2)),
             (0, 255, 0), thickness=2)

    # Draw 10 horizontal lines across the image
    for line in range(10):
        position = 10 + line * 50  # Calculate the position based on the line number

        # Draw a line across the screen
        cv2.line(frame, (10, int(position)), (frame_coordinates[1] - 10, 25 + int(position)), (0, 0, 255), thickness=3)

    return frame



video = cv2.VideoCapture("C:/Users/TH-Tech/Documents/python_projects/EW_seeker/EW_proyecto/thermal_9_hours.mp4")
flag = 0


try:
    while True:
        _, thermal_image = video.read()

        if thermal_image is None:
            break

        # only takes the region of interest, from frames
        thermal_image = thermal_image[142:622, 298:952]

        # get image dimensions
        width, height = thermal_image.shape[:2]

        # frame copy for normal visualization
        frame_normal = thermal_image

        if flag == 0:
            # form the memory blocks
            shared_thermal = shared_memory.SharedMemory(create=True, name="SharedThermal", size=width * height * 3)
            shared_normal = shared_memory.SharedMemory(create=True, name="SharedNormal", size=width * height * 3)
            shared_draw = shared_memory.SharedMemory(create=True, name="SharedDraw", size=width * height *3)

            # make the length for each memory block
            shared_image_thermal = np.ndarray(thermal_image.shape, dtype=thermal_image.dtype, buffer=shared_thermal.buf)
            shared_image_normal = np.ndarray(frame_normal.shape, dtype=frame_normal.dtype, buffer=shared_normal.buf)
            shared_image_draw = np.ndarray(thermal_image.shape, dtype=thermal_image.dtype, buffer=shared_draw.buf)
            print(f"height: {height} , width: {width} " + ", " +str(height*width*3))

            # points for colon side view
            point1_i = np.array([[5, 473], [72, 5], [384, 19], [647, 311]])  # get_four_points(thermal_image)
            point1_f = np.array([[3, 472], [2, 4], [650, 2], [649, 468]])  # get_four_points(thermal_image)

            # calculate homography matrix for both sides
            homography1, _ = cv2.findHomography(point1_i, point1_f)
            flag += 1

        if flag == 1:
            thermal_image = cv2.warpPerspective(thermal_image, homography1, (thermal_image.shape[1],thermal_image.shape[0]))

        # make the frame with thresholds
        frame_boundaries = visualization_lines(thermal_image)

        # put images into shared memory
        shared_image_thermal[:] = thermal_image[:]
        shared_image_normal[:] = frame_normal[:]
        shared_image_draw[:] = frame_boundaries[:]


    cv2.destroyAllWindows()

except KeyboardInterrupt:

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


