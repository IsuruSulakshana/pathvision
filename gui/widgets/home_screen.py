from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

class HomeScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        btn_add = QPushButton("Add New Steering Path")
        btn_existing = QPushButton("Existing Steering Paths")
        btn_compare = QPushButton("Compare Steering Path")

        btn_add.clicked.connect(lambda: self.parent.switch_screen("add"))
        btn_existing.clicked.connect(lambda: self.parent.switch_screen("existing"))
        btn_compare.clicked.connect(lambda: self.parent.switch_screen("compare"))

        layout.addWidget(btn_add)
        layout.addWidget(btn_existing)
        layout.addWidget(btn_compare)
        self.setLayout(layout)
