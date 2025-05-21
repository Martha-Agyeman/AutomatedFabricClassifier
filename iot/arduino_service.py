import serial

class ArduinoService:
    def __init__(self, port='/dev/cu.usbserial-0001', baud_rate=9600):
        self.arduino = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)  # Connection stabilization
        
    def check_for_trigger(self):
        if self.arduino.in_waiting > 0:
            line = self.arduino.readline().decode('utf-8').strip()
            print(f"Received from Arduino: '{line}'")  
            return line == "TAKE_PICTURE"
        return False
    
    def close(self):
        self.arduino.close()

