from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QMessageBox, QSizePolicy
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from backend.services.file_handler import list_vehicle_paths, load_path_data
from backend.services.comparator import compare_paths
import matplotlib.pyplot as plt
import os

class ComparePathsScreen(QWidget):
    def __init__(self, go_home_callback):
        super().__init__()
        self.go_home_callback = go_home_callback
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Path selectors ---
        selector_layout = QHBoxLayout()
        self.list_path1 = QListWidget()
        self.list_path2 = QListWidget()
        self.list_path1.setFixedWidth(280)
        self.list_path2.setFixedWidth(280)
        selector_layout.addWidget(QLabel("Select Path A:"))
        selector_layout.addWidget(self.list_path1)
        selector_layout.addWidget(QLabel("Select Path B:"))
        selector_layout.addWidget(self.list_path2)
        self.layout.addLayout(selector_layout)

        # --- Compare Button ---
        compare_btn = QPushButton("Compare Paths")
        compare_btn.setFixedWidth(150)
        compare_btn.clicked.connect(self.compare_selected_paths)
        self.layout.addWidget(compare_btn)

        # --- 3D Viewer Container ---
        viewer_container = QWidget()
        viewer_layout = QVBoxLayout()
        viewer_container.setLayout(viewer_layout)

        # Top-right toggle grid button
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

        # Matplotlib figure and canvas
        self.figure = plt.figure(figsize=(7, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumHeight(460)
        viewer_layout.addWidget(self.canvas)

        # Navigation toolbar for zoom/rotate
        self.toolbar = NavigationToolbar(self.canvas, self)
        viewer_layout.addWidget(self.toolbar)

        self.layout.addWidget(viewer_container)

        # --- Bottom Buttons ---
        button_layout = QHBoxLayout()
        back_btn = QPushButton("🔙 Back to Home")
        back_btn.clicked.connect(self.go_home_callback)
        back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(back_btn)
        self.layout.addLayout(button_layout)

        # Load available paths into lists
        self.load_paths()

    def load_paths(self):
        self.paths = list_vehicle_paths()
        self.list_path1.clear()
        self.list_path2.clear()
        for _, vehicle_name in self.paths:
            self.list_path1.addItem(vehicle_name)
            self.list_path2.addItem(vehicle_name)

    def compare_selected_paths(self):
        item1 = self.list_path1.currentItem()
        item2 = self.list_path2.currentItem()

        if not item1 or not item2:
            QMessageBox.warning(self, "Selection Error", "Please select two paths to compare.")
            return

        name1 = item1.text()
        name2 = item2.text()

        file1 = next((f[0] for f in self.paths if f[1] == name1), None)
        file2 = next((f[0] for f in self.paths if f[1] == name2), None)

        if not file1 or not file2:
            QMessageBox.critical(self, "File Error", "Selected path files could not be found.")
            return

        data1 = load_path_data(file1)
        data2 = load_path_data(file2)

        try:
            result = compare_paths(data1["segments"], data2["segments"])
        except Exception as e:
            QMessageBox.critical(self, "Comparison Error", f"Failed to compare paths:\n{e}")
            return

        self.plot_paths(result['points1'], result['points2'])

        metrics_msg = (
            f"Average Deviation: {result['avg_deviation']:.3f} units\n"
            f"Maximum Deviation: {result['max_deviation']:.3f} units"
        )
        QMessageBox.information(self, "Comparison Metrics", metrics_msg)

    def plot_paths(self, points1, points2):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.plot(*zip(*points1), label="Path A", color="blue", marker='o', linewidth=2)
        self.ax.plot(*zip(*points2), label="Path B", color="orange", marker='o', linewidth=2)
        self.ax.set_title("Steering Path Comparison")
        self.apply_axis_visibility(hidden=self.toggle_grid_btn.isChecked())
        self.ax.legend()
        self.canvas.draw()

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
