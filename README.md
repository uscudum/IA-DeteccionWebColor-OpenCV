### Guía para Detección de Color Azul en Tiempo Real con OpenCV y Flask-SocketIO

#### Objetivo:
Esta guía te llevará paso a paso a implementar un sistema de detección de color azul en tiempo real usando **OpenCV** para capturar imágenes de la cámara, y **Flask-SocketIO** para enviar actualizaciones en tiempo real a una página web que mostrará si el color azul ha sido detectado o no.

### Paso 1: Configuración del Entorno

#### 1. Instalar las librerías necesarias

Abre tu terminal y ejecuta los siguientes comandos para instalar las librerías que utilizaremos:

```bash
pip install opencv-python Flask Flask-SocketIO requests eventlet
```

### Paso 2: Creación de la Estructura del Proyecto

Crea una carpeta para el proyecto llamada `detector_color` y dentro de ella las siguientes carpetas y archivos:

```
detector_color/
├── app.py            # Código del servidor Flask
├── detector.py       # Código de detección de color en OpenCV
└── templates/
    └── index.html    # Página web para mostrar los resultados en tiempo real
```

### Paso 3: Escribir el Servidor Flask

El servidor Flask será responsable de recibir las notificaciones del cliente OpenCV y emitir mensajes en tiempo real a la página web. Crea el archivo `app.py` con el siguiente contenido:

#### Código en `app.py`:

```python
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para recibir la notificación del color azul
@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.json
    if data and 'message' in data:
        if data['message'] == 'Color azul detectado':
            socketio.emit('color_detected', {'message': 'Color azul detectado'})
        elif data['message'] == 'Color azul no detectado':
            socketio.emit('color_detected', {'message': 'No se ha detectado el color azul'})
        return 'Mensaje recibido', 200
    return 'No se recibió ningún mensaje', 400

if __name__ == "__main__":
    socketio.run(app, debug=True)
```

### Paso 4: Crear la Página Web

La página web se conectará al servidor Flask utilizando **WebSockets** y mostrará el estado de la detección de color en tiempo real. Crea el archivo `index.html` dentro de la carpeta `templates/`.

#### Código en `index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Color Detection</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
    <script type="text/javascript">
        document.addEventListener('DOMContentLoaded', (event) => {
            // Conectar al servidor de WebSockets
            var socket = io();

            // Escuchar el evento 'color_detected' desde el servidor
            socket.on('color_detected', function(data) {
                document.getElementById('status').innerText = data.message;
            });
        });
    </script>
</head>
<body>
    <h1>Detección de Color</h1>
    <p id="status">No se ha detectado el color azul</p>
</body>
</html>
```

### Paso 5: Crear el Cliente de Detección de Color (OpenCV)

El cliente en Python utilizará OpenCV para capturar imágenes de la cámara y detectar si hay color azul. Dependiendo de si se detecta o no, enviará una notificación al servidor Flask.

Crea el archivo `detector.py` con el siguiente contenido:

#### Código en `detector.py`:

```python
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
```

### Paso 6: Ejecutar el Proyecto

#### 1. Ejecuta el servidor Flask:

Abre tu terminal en la carpeta del proyecto y ejecuta el servidor Flask con:

```bash
python app.py
```

El servidor estará escuchando en `http://localhost:5000`.

#### 2. Ejecuta el cliente OpenCV:

Abre otra terminal en la misma carpeta del proyecto y ejecuta el script de detección de color:

```bash
python detector.py
```

Esto iniciará la detección de color azul desde la cámara.

#### 3. Abre la página web:

Accede a `http://localhost:5000` desde tu navegador. Verás que el mensaje en la página cambia en tiempo real dependiendo de si el color azul es detectado o no por el cliente OpenCV.

### Explicación del Funcionamiento

1. **Detección de color azul con OpenCV**: 
   - OpenCV captura frames en tiempo real desde la cámara.
   - La imagen es convertida al espacio de color HSV para aplicar una máscara que detecte el color azul.
   - Dependiendo de si se detecta azul o no, el cliente OpenCV envía una notificación al servidor Flask.

2. **Servidor Flask y WebSockets**: 
   - Flask recibe las notificaciones enviadas por el cliente.
   - El servidor usa WebSockets para notificar en tiempo real al navegador web si el color azul ha sido detectado o no.

3. **Actualización en tiempo real de la página web**: 
   - La página web se actualiza automáticamente mediante **WebSockets** sin necesidad de ser recargada manualmente.
   - El mensaje cambia entre "Color azul detectado" y "No se ha detectado el color azul" según la detección del cliente OpenCV.
