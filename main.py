from PyQt5.QtWidgets import QApplication
from gui.home import AppWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()

    # Example: access sensor screen via the dictionary if needed
    sensor_screen = window.screens.get('sensor')  # Safe access
    if sensor_screen:
        print("SensorScreen initialized successfully.")

    sys.exit(app.exec_())
