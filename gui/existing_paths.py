# gui/existing_paths.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from gui.widgets.existing_paths_screen import ExistingPathsScreen

class ExistingPathsScreenWrapper(QWidget):
    def __init__(self, go_home_callback):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(ExistingPathsScreen(go_home_callback))
        self.setLayout(layout)
