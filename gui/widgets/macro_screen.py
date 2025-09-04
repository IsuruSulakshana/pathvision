from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, QLabel,
    QPushButton, QSpinBox, QSizePolicy, QMessageBox, QListWidgetItem, QTextEdit
)
from PyQt5.QtCore import Qt
from backend.services.file_handler import list_vehicle_paths, load_path_data
from backend.services.path_math import compute_path
import os


class MacroScreen(QWidget):
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
        search_button.setFixedHeight(40)
        search_button.clicked.connect(self.filter_list)

        search_layout.addWidget(QLabel("Vehicle:"))
        search_layout.addWidget(self.vehicle_input)
        search_layout.addWidget(self.attempt_input)
        search_layout.addWidget(self.revision_input)
        search_layout.addWidget(search_button)
        self.layout.addLayout(search_layout)

        # === Vehicle List ===
        self.path_list = QListWidget()
        self.path_list.itemClicked.connect(self.generate_macro_for_item)
        self.layout.addWidget(self.path_list)

        # === Macro Preview ===
        self.macro_preview = QTextEdit()
        self.macro_preview.setReadOnly(True)
        self.macro_preview.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        self.macro_preview.setMinimumHeight(300)
        self.layout.addWidget(self.macro_preview)

        # === Bottom Buttons (larger size) ===
        button_layout = QHBoxLayout()

        generate_btn = QPushButton("📄 Generate Macro")
        # generate_btn.setFixedHeight(50)
        generate_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        generate_btn.clicked.connect(self.generate_macro_manual)
        button_layout.addWidget(generate_btn)

        back_btn = QPushButton("🔙 Back to Home")
        # back_btn.setFixedHeight(50)
        back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        back_btn.clicked.connect(self.go_home_callback)
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
            item.setData(Qt.UserRole, filename)
            self.path_list.addItem(item)

    def generate_macro_for_item(self, item):
        """Auto-generate macro when user clicks on a path in the list."""
        filename = item.data(Qt.UserRole)
        self.generate_macro_from_file(filename)

    def generate_macro_manual(self):
        """Manual button press to generate macro for selected item."""
        selected_item = self.path_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a steering path first.")
            return
        filename = selected_item.data(Qt.UserRole)
        self.generate_macro_from_file(filename)

    def generate_macro_from_file(self, filename):
        data = load_path_data(filename)
        if not data:
            QMessageBox.warning(self, "Error", f"Cannot load file: {filename}")
            return
        try:
            shaft_lengths = [seg['shaft_length'] for seg in data["segments"]]
            yaw_angles = [seg['euler'][0] for seg in data["segments"]]
            pitch_angles = [seg['euler'][1] for seg in data["segments"]]

            path_points = compute_path(shaft_lengths, yaw_angles, pitch_angles)

            # --- Build macro in SolidWorks style ---
            macro_lines = []
            macro_lines.append("' -----------------------------------------------")
            macro_lines.append("' SolidWorks Macro: Draw 3D Steering Column Path")
            macro_lines.append("' -----------------------------------------------")
            macro_lines.append("Option Explicit")
            macro_lines.append("")
            macro_lines.append("Sub main()")
            macro_lines.append("    Dim swApp As SldWorks.SldWorks")
            macro_lines.append("    Dim swModel As SldWorks.ModelDoc2")
            macro_lines.append("    Dim swSketchMgr As SldWorks.SketchManager")
            macro_lines.append("    Dim swPart As SldWorks.PartDoc")
            macro_lines.append("")
            macro_lines.append("    ' Connect to SolidWorks")
            macro_lines.append("    Set swApp = Application.SldWorks")
            macro_lines.append("    Set swModel = swApp.NewPart")
            macro_lines.append("    Set swSketchMgr = swModel.SketchManager")
            macro_lines.append("")
            macro_lines.append("    ' Start a 3D sketch")
            macro_lines.append("    swSketchMgr.Insert3DSketch True")
            macro_lines.append("")

            # Coordinates arrays
            n = len(path_points) - 1
            macro_lines.append(f"    ' Coordinates (converted to meters)")
            macro_lines.append(f"    Dim x({n}) As Double")
            macro_lines.append(f"    Dim y({n}) As Double")
            macro_lines.append(f"    Dim z({n}) As Double")
            macro_lines.append("")

            for i, (x, y, z) in enumerate(path_points):
                macro_lines.append(f"    x({i}) = {x/1000:.5f}: y({i}) = {y/1000:.5f}: z({i}) = {z/1000:.5f}")

            macro_lines.append("")
            macro_lines.append("    ' Draw lines between each point")
            macro_lines.append("    Dim i As Integer")
            macro_lines.append(f"    For i = 0 To {n-1}")
            macro_lines.append("        swSketchMgr.CreateLine x(i), y(i), z(i), x(i + 1), y(i + 1), z(i + 1)")
            macro_lines.append("    Next i")
            macro_lines.append("")
            macro_lines.append("    ' End the 3D sketch")
            macro_lines.append("    swSketchMgr.Insert3DSketch False")
            macro_lines.append("")
            macro_lines.append("    ' Zoom to fit")
            macro_lines.append("    swModel.ViewZoomtofit2")
            macro_lines.append("")
            macro_lines.append("    MsgBox \"3D Steering Column Path Sketch Created Successfully!\", vbInformation")
            macro_lines.append("End Sub")

            # Show in preview box
            self.macro_preview.setText("\n".join(macro_lines))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate macro:\n{str(e)}")

