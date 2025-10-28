# gui/widgets/add_path_screen.py
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from backend.services.file_handler import save_path_data
from backend.services.path_math import compute_path  # import our improved path logic
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

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
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["No", "Length", "X", "Y", "Z", "Sensor Position"])
        self.layout.addWidget(self.table)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Path")
        save_btn.clicked.connect(self.save_path)
        button_layout.addWidget(save_btn)

        preview_btn = QPushButton("🔍 Preview 3D Path")
        preview_btn.clicked.connect(self.preview_path)
        button_layout.addWidget(preview_btn)

        back_btn = QPushButton("🔙 Back to Home")
        back_btn.clicked.connect(self.on_back)
        button_layout.addWidget(back_btn)

        self.layout.addLayout(button_layout)

    def update_table(self):
        n = self.element_input.value()
        self.table.setRowCount(n)
        for i in range(n):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            # If sensor dropdown does not exist, create it
            if not self.table.cellWidget(i, 5):
                combo = QComboBox()
                combo.addItems(self.SENSOR_POSITIONS)
                self.table.setCellWidget(i, 5, combo)

    def collect_table_data(self):
        base = self.vehicle_base.text().strip()
        attempt = self.attempt_input.value()
        revision = self.revision_input.currentText()
        job = self.job_number.text().strip()

        if not all([base, job]):
            QMessageBox.warning(self, "Missing Info", "Please fill all vehicle info fields.")
            return None

        vehicle_id = f"{base}_attempt{attempt}_rev{revision}_job{job}".replace(" ", "_")
        n = self.element_input.value()
        segments = []

        for i in range(n):
            try:
                length_item = self.table.item(i, 1)
                x_item = self.table.item(i, 2)
                y_item = self.table.item(i, 3)
                z_item = self.table.item(i, 4)
                sensor_widget = self.table.cellWidget(i, 5)

                if not all([length_item, x_item, y_item, z_item, sensor_widget]):
                    raise ValueError(f"Row {i+1}: missing values")

                # Full float conversion (5 decimal places)
                shaft_length = float(f"{float(length_item.text()):.5f}")
                x_val = float(f"{float(x_item.text()):.5f}")
                y_val = float(f"{float(y_item.text()):.5f}")
                z_val = float(f"{float(z_item.text()):.5f}")
                sensor_pos = sensor_widget.currentText()

                segments.append({
                    "shaft_length": shaft_length,
                    "xyz": [x_val, y_val, z_val],
                    "sensor_position": sensor_pos
                })
            except Exception:
                QMessageBox.warning(self, "Invalid Data", f"Check row {i+1}: All cells must be filled with valid numbers and sensor selected.")
                return None

        return vehicle_id, segments

    def save_path(self):
        data = self.collect_table_data()
        if data:
            vehicle_id, segments = data
            try:
                save_path_data(f"{vehicle_id}.json", {"vehicle": vehicle_id, "segments": segments})
                QMessageBox.information(self, "Success", f"Path saved to:\ndata/input/{vehicle_id}.json")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def preview_path(self):
        data = self.collect_table_data()
        if not data:
            return
        _, segments = data

        # --- Extract lengths, X, Y, Z ---
        shaft_lengths = [seg["shaft_length"] for seg in segments]
        x_angles = [seg["xyz"][0] for seg in segments]
        y_angles = [seg["xyz"][1] for seg in segments]
        z_angles = [seg["xyz"][2] for seg in segments]  # included if needed in path_math

        # --- Compute 3D points ---
        points = compute_path(shaft_lengths, x_angles, y_angles)  # path_math expects yaw/pitch
        points = np.array(points)

        # --- Plot 3D path ---
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(points[:, 0], points[:, 1], points[:, 2], '-o', linewidth=2, markersize=6)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3D Steering Path Preview')
        ax.grid(True)
        ax.view_init(elev=20, azim=45)
        plt.show()
