from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox,
    QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import json
import os

class AddPathScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Steering Path")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Vehicle Model and No. of Elements
        form_layout = QHBoxLayout()

        self.vehicle_input = QLineEdit()
        self.vehicle_input.setPlaceholderText("Vehicle Model")
        form_layout.addWidget(QLabel("Vehicle Model:"))
        form_layout.addWidget(self.vehicle_input)

        self.element_input = QSpinBox()
        self.element_input.setRange(1, 100)
        self.element_input.valueChanged.connect(self.update_table)
        form_layout.addWidget(QLabel("Number of Elements:"))
        form_layout.addWidget(self.element_input)

        self.layout.addLayout(form_layout)

        # Table for Segment Data
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["No", "Length", "X", "Y", "Z"])
        self.layout.addWidget(self.table)

        # Save Button
        save_btn = QPushButton("Save Path")
        save_btn.clicked.connect(self.save_path)
        self.layout.addWidget(save_btn)

    def update_table(self):
        n = self.element_input.value()
        self.table.setRowCount(n)
        for i in range(n):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

    def save_path(self):
        vehicle = self.vehicle_input.text().strip()
        if not vehicle:
            QMessageBox.warning(self, "Missing Info", "Please enter vehicle model.")
            return

        n = self.element_input.value()
        segments = []

        for i in range(n):
            try:
                length = float(self.table.item(i, 1).text())
                x = float(self.table.item(i, 2).text())
                y = float(self.table.item(i, 3).text())
                z = float(self.table.item(i, 4).text())
                segments.append({
                    "length": length,
                    "euler": [x, y, z]
                })
            except Exception as e:
                QMessageBox.warning(self, "Invalid Data", f"Error in row {i+1}. Check all inputs.")
                return

        # Save to file
        os.makedirs("data/input", exist_ok=True)
        path_file = f"data/input/{vehicle.replace(' ', '_')}.json"
        with open(path_file, "w") as f:
            json.dump(segments, f, indent=2)

        QMessageBox.information(self, "Saved", f"Path saved to: {path_file}")
