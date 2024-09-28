import os
import serial 

class SerialCommunication:
    def __init__(self, device_path):
        self.device_path = str(device_path)
        self.baud_rate = 9600
        self.ser = None
        self.serial_connected = False
    
    def connect_serial(self):
        if os.path.exists(self.device_path):
            self.ser = serial.Serial(self.device_path, self.baud_rate)
            self.serial_connected = True
            return print(f'Successfully connected to {self.device_path}')
        else:
           return print(f'Serial {self.device_path} is not available')
        
    def sanitise_message(self, message):
    # Replace ellipsis with three full stops
        message = str(message)
        message = message.replace('…', '...')
        # Filter out non-ASCII characters or replace them with '?'
        return ''.join([char if ord(char) < 128 else '?' for char in message])

    def send_serial(self, message):
        if self.serial_connected:
            try:
                sanitised_message = self.sanitise_message(message)
                text = str(sanitised_message) +'\n'
                self.ser.write(bytes(text.encode('ascii')))
            except serial.SerialException as e:
                print(f'{self.device_path} SERIAL ERROR: {e}')
                pass
            except Exception as e:
                print(f'serial not working: {e}')



    def close_serial(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                print('Serial connection closed')
            except Exception as e:
                print(f'Error closing serial connection: {e}')