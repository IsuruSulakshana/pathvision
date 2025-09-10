import serial
import struct
import threading
from PyQt5.QtCore import QObject, pyqtSignal

class WitMotionReader(QObject):
    angles_updated = pyqtSignal(float, float, float)  # roll, pitch, yaw

    def __init__(self, port="COM3", baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False

    def start(self):
        """Start the serial reader thread."""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            threading.Thread(target=self.read_loop, daemon=True).start()
        except serial.SerialException as e:
            print(f"[ERROR] Could not open port {self.port}: {e}")

    def stop(self):
        """Stop reading and close port."""
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()

    def read_loop(self):
        """Continuously read packets from sensor."""
        while self.running and self.serial and self.serial.is_open:
            header = self.serial.read(1)
            if header == b'\x55':  # Start byte
                type_byte = self.serial.read(1)
                if type_byte == b'\x53':  # Euler angles packet
                    data = self.serial.read(8)  # 8 bytes payload
                    checksum = self.serial.read(1)  # checksum
                    if len(data) == 8:
                        roll_raw, pitch_raw, yaw_raw, temp_raw = struct.unpack('<hhhh', data)
                        roll = roll_raw / 32768.0 * 180.0
                        pitch = pitch_raw / 32768.0 * 180.0
                        yaw = yaw_raw / 32768.0 * 180.0
                        self.angles_updated.emit(roll, pitch, yaw)
