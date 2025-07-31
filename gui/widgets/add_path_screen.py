from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
)
from backend.services.file_handler import save_path_data
from PyQt5.QtCore import Qt


class AddPathScreen(QWidget):
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
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["No", "Length", "X", "Y", "Z"])
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
            # Set row number
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

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
                shaft_length_item = self.table.item(i, 1)
                x_item = self.table.item(i, 2)
                y_item = self.table.item(i, 3)
                z_item = self.table.item(i, 4)

                if not all([shaft_length_item, x_item, y_item, z_item]):
                    raise ValueError("Empty cell")

                shaft_length = float(shaft_length_item.text())
                x = float(x_item.text())
                y = float(y_item.text())
                z = float(z_item.text())

                segments.append({
                    "shaft_length": shaft_length,
                    "euler": [x, y, z]
                })

            except Exception:
                QMessageBox.warning(self, "Invalid Data", f"Check row {i+1}: All cells must be filled and valid numbers.")
                return

        # Build final JSON data
        data = {
            "vehicle": vehicle_id,
            "segments": segments
        }

        try:
            save_path_data(f"{vehicle_id}.json", data)
            QMessageBox.information(self, "Success", f"Path saved to:\ndata/input/{vehicle_id}.json")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
