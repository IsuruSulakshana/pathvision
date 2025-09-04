import serial
import threading
import time

class SensorReader:
    def __init__(self, port="COM4", baudrate=9600, callback=None):
        self.port = port
        self.baudrate = baudrate
        self.callback = callback
        self.running = False
        self.ser = None

        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            print(f"[INFO] Opened serial port {port} at {baudrate} baud")
        except serial.SerialException as e:
            print(f"[ERROR] Could not open serial port {port}: {e}")

    def start(self):
        if self.ser:
            self.running = True
            threading.Thread(target=self.read_loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()

    def read_loop(self):
        initializing = True
        while self.running:
            if self.ser.in_waiting >= 11:  # Example minimum packet length
                packet = self.ser.read(11)  # Read packet bytes
                # For now, just mark first valid packet as initialized
                if initializing:
                    initializing = False
                    if self.callback:
                        self.callback("Sensor Ready")
                # TODO: Parse packet into actual sensor values here
            else:
                if initializing and self.callback:
                    self.callback("Initializing sensor...")
            time.sleep(0.05)
