from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

class HomeScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        btn_add = QPushButton("➕ Add New Steering Path")
        btn_existing = QPushButton("📁 Existing Steering Paths")
        btn_compare = QPushButton("🔍 Compare Steering Path")
        btn_sensor = QPushButton("📡 View Sensor Data")   # <-- NEW BUTTON
        btn_macro = QPushButton("⚙️ Generate Macro")   # <-- NEW BUTTON


        btn_add.clicked.connect(lambda: self.parent.switch_screen("add"))
        btn_existing.clicked.connect(lambda: self.parent.switch_screen("existing"))
        btn_compare.clicked.connect(lambda: self.parent.switch_screen("compare"))
        btn_sensor.clicked.connect(lambda: self.parent.switch_screen("sensor"))  # <-- NEW ACTION
        btn_macro.clicked.connect(lambda: self.parent.switch_screen("macro"))  # <-- NEW ACTION

        layout.addWidget(btn_add)
        layout.addWidget(btn_existing)
        layout.addWidget(btn_compare)
        layout.addWidget(btn_sensor)   # <-- ADD TO LAYOUT
        layout.addWidget(btn_macro)   # <-- ADD TO LAYOUT
        
        self.setLayout(layout)
