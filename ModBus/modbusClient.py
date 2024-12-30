
import serial
import random
import time
import struct
import json

# Funzione per calcolare il CRC Modbus
def calculate_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

# Funzione per creare un frame Modbus RTU
def create_modbus_frame(slave_id, function_code, start_address, values):
    frame = struct.pack('>B', slave_id)  # Slave ID
    frame += struct.pack('>B', function_code)  # Function Code
    frame += struct.pack('>H', start_address)  # Start Address
    frame += struct.pack('>H', len(values))  # Number of Registers
    for value in values:
        frame += struct.pack('>H', value)  # Register Value
    crc = calculate_crc(frame)
    frame += struct.pack('<H', crc)  # CRC
    return frame

# Funzione per leggere il file di configurazione JSON
def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

# Funzione per leggere i dati dalla seriale
def read_from_serial(ser):
   if ser.in_waiting > 0:  # Verifica se ci sono dati disponibili
        data = ser.read(ser.in_waiting)  # Legge tutti i dati disponibili
        try:
            slave_id, function_code, start_address, values = parse_modbus_frame(data)
            print(f"Frame ricevuto:\n"
                  f"  Slave ID: {slave_id}\n"
                  f"  Function Code: {function_code}\n"
                  f"  Start Address: {start_address}\n"
                  f"  Values: {values}")
        except ValueError as e:
            print(f"Errore nella decodifica del frame: {e}")
        return data
    #return None
 
 #Parser della stringa ricevuta
def parse_modbus_frame(data):
    if len(data) < 8:  # Lunghezza minima di un frame Modbus valido
        raise ValueError("Frame Modbus troppo corto")

    # Estrai slave_id, function_code e byte_count
    slave_id = data[0]
    function_code = data[1]
    start_address = struct.unpack('>H', data[2:4])[0]
    register_count = struct.unpack('>H', data[4:6])[0]

    # Calcola il CRC per verificare l'integrità
    crc_received = struct.unpack('<H', data[-2:])[0]
    crc_calculated = calculate_crc(data[:-2])
    if crc_received != crc_calculated:
        raise ValueError(f"Errore CRC: calcolato {crc_calculated}, ricevuto {crc_received}")

    # Decodifica i valori dei registri
    values = []
    for i in range(6, len(data) - 2, 2):
        values.append(struct.unpack('>H', data[i:i + 2])[0])

    return slave_id, function_code, start_address, values



# Funzione principale
def main():
    # Carica la configurazione
    config = load_config('E:\\Python\\config.json')
    #config = load_config('config.json')
    serial_config = config['serial']
    modbus_config = config['modbus']

    # Configura la porta seriale
    port = serial_config['port']
    baudrate = serial_config['baudrate']
    timeout = serial_config['timeout']

    slave_id = modbus_config['slave_id']
    start_address = modbus_config['start_address']
    register_count = modbus_config['register_count']

    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            print(f"Server Modbus RTU avviato su {port} a {baudrate} baud.")

            while True:
                # Genera valori casuali per i registri
                values = [random.randint(0, 65535) for _ in range(register_count)]

                # Crea il frame Modbus RTU
                frame = create_modbus_frame(slave_id, 3, start_address, values)

                # Invia il frame sulla porta seriale
                ser.write(frame)
                print(f"Inviato frame: {frame.hex()} con valori {values}")

                # Legge i dati dalla porta seriale (se disponibili)
                received_data = read_from_serial(ser)
                if received_data:
                    print(f"Conferma ricezione: ")
                    parse_modbus_frame(received_data)

                time.sleep(1)  # Aspetta 1 secondo prima del prossimo invio

    except serial.SerialException as e:
        print(f"Errore con la porta seriale: {e}")
    except KeyboardInterrupt:
        print("Interrotto manualmente dall'utente.")

# Esegue il server
if __name__ == '__main__':
    main()

