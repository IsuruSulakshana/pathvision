from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QStackedWidget, QApplication, QSizePolicy
)
from gui.widgets.add_path_screen import AddPathScreen
from gui.widgets.existing_paths_screen import ExistingPathsScreen
from gui.widgets.compare_paths_screen import ComparePathsScreen


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚘 PathVision")
        self.setMinimumSize(800, 600)

        self.stack = QStackedWidget()
        self.home_widget = QWidget()
        self.stack.addWidget(self.home_widget)

        # Other screens
        self.add_path_screen = AddPathScreen(self.go_home)
        self.existing_paths_screen = ExistingPathsScreen(self.go_home)
        self.compare_paths_screen = ComparePathsScreen(self.go_home)

        self.stack.addWidget(self.add_path_screen)
        self.stack.addWidget(self.existing_paths_screen)
        self.stack.addWidget(self.compare_paths_screen)

        self.init_home_ui()
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def init_home_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Button style
        button_style = """
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                min-width: 200px;
                max-width: 300px;
            }
        """

        btn_add = QPushButton("➕ Add New Path")
        btn_add.setStyleSheet(button_style)
        btn_add.clicked.connect(self.show_add_path)

        btn_existing = QPushButton("📁 View Existing Paths")
        btn_existing.setStyleSheet(button_style)
        btn_existing.clicked.connect(self.show_existing_paths)

        btn_compare = QPushButton("🔍 Compare Paths")
        btn_compare.setStyleSheet(button_style)
        btn_compare.clicked.connect(self.show_compare_paths)

        # Centered buttons
        for btn in [btn_add, btn_existing, btn_compare]:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(btn, alignment=Qt.AlignHCenter)

        self.home_widget.setLayout(layout)

    def show_add_path(self):
        self.stack.setCurrentWidget(self.add_path_screen)

    def show_existing_paths(self):
        self.stack.setCurrentWidget(self.existing_paths_screen)

    def show_compare_paths(self):
        self.stack.setCurrentWidget(self.compare_paths_screen)

    def go_home(self):
        self.stack.setCurrentWidget(self.home_widget)
