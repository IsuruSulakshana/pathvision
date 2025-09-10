# gui/widgets/sensor_screen.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class SensorScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sensor Screen")
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Status label
        self.status_label = QLabel("Status: Not connected")
        self.status_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.status_label)

        # Angle labels
        self.pitch_label = QLabel("Pitch: 0.0°")
        self.pitch_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.pitch_label)

        self.yaw_label = QLabel("Yaw: 0.0°")
        self.yaw_label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.yaw_label)

        # Back button
        self.back_button = QPushButton("Back to Home")
        self.back_button.setObjectName("btn_primary")
        layout.addWidget(self.back_button, alignment=Qt.AlignHCenter)

    # Called by sensor_reader
    def update_angles(self, pitch, yaw):
        self.pitch_label.setText(f"Pitch: {pitch:.2f}°")
        self.yaw_label.setText(f"Yaw: {yaw:.2f}°")

    def update_status(self, text):
        self.status_label.setText(f"Status: {text}")
