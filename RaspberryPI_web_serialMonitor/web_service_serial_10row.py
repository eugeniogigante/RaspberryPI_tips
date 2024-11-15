from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import serial
import threading

# Configurazione Flask e SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Configurazione seriale
serial_port = '/dev/ttyS0'  # Porta seriale per il Raspberry Pi
baud_rate = 9600             # Baud rate iniziale
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Variabile per salvare le righe lette
data_lines = []

# Funzione per leggere continuamente dalla seriale
def read_serial():
    global data_lines
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            data_lines.append(line)
            # Limita a 10 righe
            data_lines = data_lines[-10:]
            socketio.emit('update_data', {'data': data_lines})

# Avvio del thread di lettura seriale
threading.Thread(target=read_serial, daemon=True).start()

# Rotta per la pagina principale
@app.route('/')
def index():
    return render_template('index_serial_10row.html')

# Rotta per aggiornare il baud rate
@app.route('/set_baudrate', methods=['POST'])
def set_baudrate():
    global baud_rate, ser
    new_baudrate = int(request.form.get('baudrate'))
    ser.close()
    ser = serial.Serial(serial_port, new_baudrate, timeout=1)
    baud_rate = new_baudrate
    return jsonify({'status': 'success', 'baudrate': baud_rate})

# Avvio dell'app Flask
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
