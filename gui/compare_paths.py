# gui/compare_paths.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from gui.widgets.compare_paths_screen import ComparePathsScreen

class ComparePaths(QWidget):
    def __init__(self, go_home_callback):
        super().__init__()
        self.go_home_callback = go_home_callback
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.compare_screen = ComparePathsScreen(go_home_callback)
        self.layout.addWidget(self.compare_screen)
