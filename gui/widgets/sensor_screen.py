from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from backend.services.sensor_reader import SensorReader

class SensorScreen(QWidget):
    def __init__(self, go_home_callback):
        super().__init__()
        self.go_home_callback = go_home_callback

        layout = QVBoxLayout()
        self.label = QLabel("Initializing sensor...")
        self.label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.label)

        self.btn_home = QPushButton("⬅ Back to Home")
        self.btn_home.clicked.connect(self.go_home)
        layout.addWidget(self.btn_home, alignment=Qt.AlignHCenter)

        self.setLayout(layout)

        # Start sensor reader
        self.reader = SensorReader(port="COM4", baudrate=9600, callback=self.update_label)
        self.reader.start()

    def update_label(self, text):
        self.label.setText(text)

    def go_home(self):
        self.reader.stop()
        self.go_home_callback()
