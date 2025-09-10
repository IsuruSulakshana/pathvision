import serial
import threading
import time

class SensorReader:
    def __init__(self, port, baudrate, angle_callback, status_callback):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.thread = None
        self.running = False
        self.angle_callback = angle_callback      # expects update_angles(pitch, yaw)
        self.status_callback = status_callback    # expects update_status(message)

    def start(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            self.status_callback(f"Opened serial port {self.port} at {self.baudrate} baud")
        except Exception as e:
            self.status_callback(f"[ERROR] Could not open serial port {self.port}: {e}")
            return

        self.running = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()

    def read_loop(self):
        """Read from sensor continuously."""
        self.status_callback("Initializing sensor...")

        while self.running:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    # Example: assume CSV format "pitch,yaw"
                    parts = line.split(",")
                    if len(parts) == 2:
                        pitch = float(parts[0])
                        yaw = float(parts[1])
                        self.angle_callback(pitch, yaw)
            except Exception as e:
                self.status_callback(f"Read error: {e}")
            time.sleep(0.01)

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.status_callback("Serial port closed")
