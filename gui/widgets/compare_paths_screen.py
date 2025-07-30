from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QMessageBox, QSizePolicy, QLineEdit, QSpinBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from backend.services.file_handler import list_vehicle_paths, load_path_data
from backend.services.comparator import compare_paths
import matplotlib.pyplot as plt

class ComparePathsScreen(QWidget):
    def __init__(self, go_home_callback):
        super().__init__()
        self.go_home_callback = go_home_callback
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # === Two selectors with search ===
        selectors_layout = QHBoxLayout()

        # Create search + list widget for Path A
        self.pathA_widget = self.create_searchable_path_selector("Path A")
        selectors_layout.addLayout(self.pathA_widget['layout'])

        # Create search + list widget for Path B
        self.pathB_widget = self.create_searchable_path_selector("Path B")
        selectors_layout.addLayout(self.pathB_widget['layout'])

        self.layout.addLayout(selectors_layout)

        # --- Compare Button near top right controls (skip here, add in viewer) ---

        # --- 3D Viewer Container ---
        viewer_container = QWidget()
        viewer_layout = QVBoxLayout()
        viewer_container.setLayout(viewer_layout)

        # Top-right control buttons layout
        top_right_layout = QHBoxLayout()
        top_right_layout.addStretch()

        # Compare Button
        compare_btn = QPushButton("🧮 Compare Paths")
        compare_btn.setObjectName("primaryButton")
        compare_btn.setFixedHeight(32)
        compare_btn.setMinimumWidth(130)
        compare_btn.clicked.connect(self.compare_selected_paths)
        top_right_layout.addWidget(compare_btn)

        # Toggle Grid Button
        self.toggle_grid_btn = QPushButton("🧱 Hide Grid")
        self.toggle_grid_btn.setCheckable(True)
        self.toggle_grid_btn.setChecked(False)
        self.toggle_grid_btn.clicked.connect(self.toggle_grid_walls)
        self.toggle_grid_btn.setObjectName("primaryButton")
        self.toggle_grid_btn.setFixedHeight(32)
        self.toggle_grid_btn.setMinimumWidth(100)
        top_right_layout.addWidget(self.toggle_grid_btn)

        viewer_layout.addLayout(top_right_layout)

        # Matplotlib figure and canvas
        self.figure = plt.figure(figsize=(7, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumHeight(460)
        viewer_layout.addWidget(self.canvas)

        # Navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        viewer_layout.addWidget(self.toolbar)

        self.layout.addWidget(viewer_container)

    
        # --- Bottom Buttons (Responsive Full Width, Equal Size) ---
        button_layout = QHBoxLayout()

        # Create Report Button
        report_btn = QPushButton("📄 Create Report")
        report_btn.setObjectName("primaryButton")
        report_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Back to Home Button
        back_btn = QPushButton("🔙 Back to Home")
        back_btn.clicked.connect(self.go_home_callback)
        back_btn.setObjectName("primaryButton")
        back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Add buttons with equal stretch
        button_layout.addStretch(1)
        button_layout.addWidget(report_btn, stretch=5)
        button_layout.addSpacing(20)
        button_layout.addWidget(back_btn, stretch=5)
        button_layout.addStretch(1)

        self.layout.addLayout(button_layout)


        # Load paths initially (for both selectors)
        self.all_paths = list_vehicle_paths()
        self.load_paths_in_selector(self.pathA_widget)
        self.load_paths_in_selector(self.pathB_widget)

    def create_searchable_path_selector(self, title):
        """Returns dict with layout and widgets for one path selector with search inputs"""
        layout = QVBoxLayout()

        # Title label
        layout.addWidget(QLabel(f"Select {title}:"))

        # Search controls layout
        search_layout = QHBoxLayout()

        vehicle_input = QLineEdit()
        vehicle_input.setPlaceholderText("Brand|Model|Gen")
        vehicle_input.setFixedWidth(200)

        attempt_input = QSpinBox()
        attempt_input.setMinimum(0)
        attempt_input.setMaximum(99)
        attempt_input.setPrefix("Attempt ")
        attempt_input.setFixedWidth(110)

        revision_input = QSpinBox()
        revision_input.setMinimum(0)
        revision_input.setMaximum(9)
        revision_input.setPrefix("Rev ")
        revision_input.setFixedWidth(90)

        search_button = QPushButton("🔍 Search")
        search_button.setFixedWidth(80)

        search_layout.addWidget(vehicle_input)
        search_layout.addWidget(attempt_input)
        search_layout.addWidget(revision_input)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        # List widget for paths
        list_widget = QListWidget()
        layout.addWidget(list_widget)

        # Connect search button to filter function
        search_button.clicked.connect(lambda: self.filter_selector_list(
            vehicle_input.text(), attempt_input.value(), revision_input.value(), list_widget))

        return {
            'layout': layout,
            'vehicle_input': vehicle_input,
            'attempt_input': attempt_input,
            'revision_input': revision_input,
            'search_button': search_button,
            'list_widget': list_widget,
        }

    def load_paths_in_selector(self, selector):
        """Load all vehicle names into selector's list widget"""
        selector['list_widget'].clear()
        for _, vehicle in self.all_paths:
            selector['list_widget'].addItem(vehicle)

    def filter_selector_list(self, vehicle_text, attempt, revision, list_widget):
        """Filter all_paths by inputs and update the given list widget"""
        search_key = f"{vehicle_text.strip()}_attempt{attempt}_rev{revision}".lower()
        filtered = [p for p in self.all_paths if search_key in p[1].lower()]
        list_widget.clear()
        for _, vehicle in filtered:
            list_widget.addItem(vehicle)

    def compare_selected_paths(self):
        # Get selections from both selectors
        item1 = self.pathA_widget['list_widget'].currentItem()
        item2 = self.pathB_widget['list_widget'].currentItem()

        if not item1 or not item2:
            QMessageBox.warning(self, "Selection Error", "Please select two paths to compare.")
            return

        name1 = item1.text()
        name2 = item2.text()

        file1 = next((f[0] for f in self.all_paths if f[1] == name1), None)
        file2 = next((f[0] for f in self.all_paths if f[1] == name2), None)

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
