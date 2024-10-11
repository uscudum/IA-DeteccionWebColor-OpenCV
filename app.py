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

