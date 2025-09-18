# gui/widgets/home_screen.py

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy


class HomeScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Common button style
        button_style = """
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                min-width: 200px;
                max-width: 300px;
            }
        """

        # Create buttons
        btn_add = QPushButton("➕ Add New Path")
        btn_existing = QPushButton("📁 View Existing Paths")
        btn_compare = QPushButton("🔍 Compare Paths")
        btn_sensor = QPushButton("📡 View Sensor Data")
        btn_macro = QPushButton("⚙️ Generate Macro")
        btn_shaftsync = QPushButton("🔄 ShaftSync Encoders)")  # NEW

        # Apply style
        for btn in [btn_add, btn_existing, btn_compare, btn_sensor, btn_macro, btn_shaftsync]:
            btn.setStyleSheet(button_style)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(btn, alignment=Qt.AlignHCenter)

        # Connect buttons to parent switch_screen
        btn_add.clicked.connect(lambda: self.parent.switch_screen("add"))
        btn_existing.clicked.connect(lambda: self.parent.switch_screen("existing"))
        btn_compare.clicked.connect(lambda: self.parent.switch_screen("compare"))
        btn_sensor.clicked.connect(lambda: self.parent.switch_screen("sensor"))
        btn_macro.clicked.connect(lambda: self.parent.switch_screen("macro"))
        btn_shaftsync.clicked.connect(lambda: self.parent.switch_screen("shaftsync"))  # NEW

        self.setLayout(layout)
