from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, QLabel,
    QPushButton, QSpinBox, QSizePolicy, QMessageBox, QListWidgetItem
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from backend.services.file_handler import list_vehicle_paths, load_path_data
from backend.services.path_math import compute_path
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os

class ExistingPathsScreen(QWidget):
    def __init__(self, go_home_callback):
        super().__init__()
        self.go_home_callback = go_home_callback
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # === Search Inputs ===
        search_layout = QHBoxLayout()
        self.vehicle_input = QLineEdit()
        self.vehicle_input.setPlaceholderText("Brand|Model|Gen")
        self.vehicle_input.setFixedWidth(250)

        self.attempt_input = QSpinBox()
        self.attempt_input.setMinimum(0)
        self.attempt_input.setMaximum(99)
        self.attempt_input.setPrefix("Attempt ")
        self.attempt_input.setFixedWidth(120)

        self.revision_input = QSpinBox()
        self.revision_input.setMinimum(0)
        self.revision_input.setMaximum(9)
        self.revision_input.setPrefix("Rev ")
        self.revision_input.setFixedWidth(100)

        search_button = QPushButton("🔍 Search")
        search_button.clicked.connect(self.filter_list)

        search_layout.addWidget(QLabel("Vehicle:"))
        search_layout.addWidget(self.vehicle_input)
        search_layout.addWidget(self.attempt_input)
        search_layout.addWidget(self.revision_input)
        search_layout.addWidget(search_button)
        self.layout.addLayout(search_layout)

        # === Vehicle List ===
        self.path_list = QListWidget()
        self.path_list.itemClicked.connect(self.display_3d_path)
        self.layout.addWidget(self.path_list)

        # === 3D Viewer with Grid Toggle ===
        viewer_layout = QVBoxLayout()
        viewer_container = QWidget()
        viewer_container.setLayout(viewer_layout)

        top_right_layout = QHBoxLayout()
        top_right_layout.addStretch()

        self.toggle_grid_btn = QPushButton("Hide Grid")
        self.toggle_grid_btn.setCheckable(True)
        self.toggle_grid_btn.setChecked(False)
        self.toggle_grid_btn.clicked.connect(self.toggle_grid_walls)
        self.toggle_grid_btn.setFixedWidth(100)
        self.toggle_grid_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 2px;
            }
            QPushButton:checked {
                background-color: #888;
            }
        """)
        top_right_layout.addWidget(self.toggle_grid_btn)
        viewer_layout.addLayout(top_right_layout)

        self.figure = plt.figure(figsize=(7, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumHeight(460)
        viewer_layout.addWidget(self.canvas)

        self.layout.addWidget(viewer_container)

        # === Bottom Buttons ===
        button_layout = QHBoxLayout()
        delete_btn = QPushButton("🗑️ Delete Path")
        delete_btn.clicked.connect(self.delete_selected_path)
        delete_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(delete_btn)

        back_btn = QPushButton("🔙 Back to Home")
        back_btn.clicked.connect(self.go_home_callback)
        back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(back_btn)

        self.layout.addLayout(button_layout)

        # Load paths initially
        self.refresh()

    def refresh(self):
        """Reload all paths into the list."""
        self.paths = list_vehicle_paths()
        self.filtered_paths = self.paths.copy()
        self.populate_list(self.filtered_paths)

    def filter_list(self):
        base = self.vehicle_input.text().strip()
        attempt = self.attempt_input.value()
        revision = self.revision_input.value()
        search_key = f"{base}_attempt{attempt}_rev{revision}".lower()
        self.filtered_paths = [p for p in self.paths if search_key in p[1].lower()]
        self.populate_list(self.filtered_paths)

    def populate_list(self, path_data_list):
        """Fill the list widget with vehicle names only but store filenames internally."""
        self.path_list.clear()
        for filename, vehicle in path_data_list:
            item = QListWidgetItem(vehicle)
            item.setData(Qt.UserRole, filename)  # store the filename invisibly
            self.path_list.addItem(item)

    def display_3d_path(self, item):
        filename = item.data(Qt.UserRole)
        data = load_path_data(filename)
        if not data:
            QMessageBox.warning(self, "Error", f"Cannot load file: {filename}")
            return
        try:
            shaft_lengths = [seg['shaft_length'] for seg in data["segments"]]
            yaw_angles = [seg['euler'][0] for seg in data["segments"]]
            pitch_angles = [seg['euler'][1] for seg in data["segments"]]

            path_points = compute_path(shaft_lengths, yaw_angles, pitch_angles)
            xs = [p[0] for p in path_points]
            ys = [p[1] for p in path_points]
            zs = [p[2] for p in path_points]

            self.figure.clear()
            self.ax = self.figure.add_subplot(111, projection='3d')
            self.ax.plot(xs, ys, zs, marker='o', linewidth=2, color='red')
            self.ax.set_title(data.get("vehicle", "Steering Path"))

            self.apply_axis_visibility(hidden=self.toggle_grid_btn.isChecked())
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to plot path:\n{str(e)}")

    def toggle_grid_walls(self):
        hidden = self.toggle_grid_btn.isChecked()
        self.toggle_grid_btn.setText("Show Grid" if hidden else "Hide Grid")
        self.apply_axis_visibility(hidden)
        self.canvas.draw()

    def apply_axis_visibility(self, hidden):
        if not hasattr(self, 'ax'):
            return
        if hidden:
            self.ax.set_axis_off()
            self.ax.grid(False)
        else:
            self.ax.set_axis_on()
            self.ax.grid(True)
            self.ax.set_xlabel("X")
            self.ax.set_ylabel("Y")
            self.ax.set_zlabel("Z")

    def delete_selected_path(self):
        selected_item = self.path_list.currentItem()
        if not selected_item:
            return
        vehicle_name = selected_item.text()
        filename = selected_item.data(Qt.UserRole)
        filepath = os.path.join("data/input", filename)

        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{vehicle_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        try:
            os.remove(filepath)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete file:\n{e}")
