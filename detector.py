import cv2
import numpy as np
import requests

# URL del servidor al que se enviará la notificación
url = 'http://localhost:5000/upload'

# Inicia la captura de la cámara
cap = cv2.VideoCapture(0)

# Definir el rango del color azul en el espacio de color HSV
lower_blue = np.array([100, 150, 0])
upper_blue = np.array([140, 255, 255])

# Variable para almacenar el estado previo (para evitar enviar notificaciones repetitivas)
was_blue_detected = False

while True:
    # Lee un frame de la cámara
    ret, frame = cap.read()

    # Convertir el frame de BGR a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Crear una máscara que detecte el color azul
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Contar los píxeles azules en la máscara
    blue_pixels = cv2.countNonZero(mask)

    # Muestra el frame capturado y la máscara
    cv2.imshow('Camera', frame)
    cv2.imshow('Mask', mask)

    # Si se detectan suficientes píxeles azules, enviar la notificación de que se detectó
    if blue_pixels > 500:
        if not was_blue_detected:
            data = {'message': 'Color azul detectado'}
            try:
                requests.post(url, json=data)
                was_blue_detected = True
            except Exception as e:
                print(f"Error enviando la notificación: {e}")
    else:
        # Si ya no se detecta el color azul, enviar la notificación de que no se detecta más
        if was_blue_detected:
            data = {'message': 'Color azul no detectado'}
            try:
                requests.post(url, json=data)
                was_blue_detected = False
            except Exception as e:
                print(f"Error enviando la notificación: {e}")

    # Si presionas 'q', se cierra la ventana
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera la cámara y cierra las ventanas
cap.release()
cv2.destroyAllWindows()
