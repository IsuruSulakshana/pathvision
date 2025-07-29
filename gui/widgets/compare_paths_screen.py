from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton

class ComparePathsScreen(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back

        layout = QVBoxLayout()
        layout.addWidget(QLabel("📊 Compare Paths Screen"))

        back_btn = QPushButton("🔙 Back to Home")
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn)

        self.setLayout(layout)
