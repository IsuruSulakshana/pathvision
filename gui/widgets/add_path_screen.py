from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
)
from backend.services.file_handler import save_path_data
from PyQt5.QtCore import Qt

class AddPathScreen(QWidget):
    SENSOR_POSITIONS = ["A", "B", "C", "D"]  # Available sensor positions

    def __init__(self, on_back):
        super().__init__()
        self.setWindowTitle("Add New Steering Path")
        self.on_back = on_back
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Vehicle ID Section ---
        vehicle_layout = QHBoxLayout()
        self.vehicle_base = QLineEdit()
        self.vehicle_base.setPlaceholderText("brand|model|gen")
        vehicle_layout.addWidget(QLabel("Vehicle:"))
        vehicle_layout.addWidget(self.vehicle_base)

        self.attempt_input = QSpinBox()
        self.attempt_input.setRange(1, 999)
        vehicle_layout.addWidget(QLabel("Attempt:"))
        vehicle_layout.addWidget(self.attempt_input)

        self.revision_input = QComboBox()
        self.revision_input.addItems([str(i) for i in range(10)])
        vehicle_layout.addWidget(QLabel("Revision:"))
        vehicle_layout.addWidget(self.revision_input)

        self.job_number = QLineEdit()
        self.job_number.setPlaceholderText("Job No.")
        vehicle_layout.addWidget(QLabel("Job No:"))
        vehicle_layout.addWidget(self.job_number)
        self.layout.addLayout(vehicle_layout)

        # --- Element Count ---
        count_layout = QHBoxLayout()
        self.element_input = QSpinBox()
        self.element_input.setRange(1, 100)
        self.element_input.valueChanged.connect(self.update_table)
        count_layout.addWidget(QLabel("Number of Elements:"))
        count_layout.addWidget(self.element_input)
        self.layout.addLayout(count_layout)

        # --- Segment Table ---
        self.table = QTableWidget(0, 6)  # Add 6th column for Sensor Position
        self.table.setHorizontalHeaderLabels(["No", "Length", "X", "Y", "Z", "Sensor Position"])
        self.layout.addWidget(self.table)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Path")
        save_btn.clicked.connect(self.save_path)
        button_layout.addWidget(save_btn)

        back_btn = QPushButton("🔙 Back to Home")
        back_btn.clicked.connect(self.on_back)
        button_layout.addWidget(back_btn)

        self.layout.addLayout(button_layout)

    def update_table(self):
        n = self.element_input.value()
        self.table.setRowCount(n)
        for i in range(n):
            # Row number
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

            # If sensor dropdown does not exist, create it
            if not self.table.cellWidget(i, 5):
                combo = QComboBox()
                combo.addItems(self.SENSOR_POSITIONS)
                combo.currentTextChanged.connect(lambda val, row=i: self.adjust_pitch(row, val))
                self.table.setCellWidget(i, 5, combo)

    def adjust_pitch(self, row, sensor_position):
        """Adjust the Y value (pitch) based on sensor position."""
        y_item = self.table.item(row, 3)  # Y is column index 3
        if y_item is None:
            return
        try:
            y_val = float(y_item.text())
        except ValueError:
            return

        # Apply sensor position adjustment
        if sensor_position == "A":
            adjusted = y_val
        elif sensor_position == "B":
            adjusted = y_val - 90
        elif sensor_position == "C":
            adjusted = y_val - 180
        elif sensor_position == "D":
            adjusted = y_val + 90
        else:
            adjusted = y_val

        y_item.setText(str(adjusted))


    def save_path(self):
        base = self.vehicle_base.text().strip()
        attempt = self.attempt_input.value()
        revision = self.revision_input.currentText()
        job = self.job_number.text().strip()

        if not all([base, job]):
            QMessageBox.warning(self, "Missing Info", "Please fill all vehicle info fields.")
            return

        vehicle_id = f"{base}_attempt{attempt}_rev{revision}_job{job}".replace(" ", "_")
        n = self.element_input.value()
        segments = []

        for i in range(n):
            try:
                length_item = self.table.item(i, 1)
                x_item = self.table.item(i, 2)
                y_item = self.table.item(i, 3)
                pitch_item = self.table.item(i, 4)
                sensor_widget = self.table.cellWidget(i, 5)

                if not all([length_item, x_item, y_item, pitch_item, sensor_widget]):
                    raise ValueError("Empty cell or missing sensor")

                shaft_length = float(length_item.text())
                x = float(x_item.text())
                y = float(y_item.text())
                pitch = float(pitch_item.text())
                sensor_pos = sensor_widget.currentText()

                segments.append({
                    "shaft_length": shaft_length,
                    "euler": [x, y, pitch],
                    "sensor_position": sensor_pos
                })
            except Exception:
                QMessageBox.warning(self, "Invalid Data", f"Check row {i+1}: All cells must be filled with valid numbers and sensor selected.")
                return

        data = {"vehicle": vehicle_id, "segments": segments}

        try:
            save_path_data(f"{vehicle_id}.json", data)
            QMessageBox.information(self, "Success", f"Path saved to:\ndata/input/{vehicle_id}.json")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
