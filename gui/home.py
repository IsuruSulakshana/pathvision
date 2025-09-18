# app_window.py

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QSizePolicy, QPushButton
from gui.widgets.add_path_screen import AddPathScreen
from gui.widgets.existing_paths_screen import ExistingPathsScreen
from gui.widgets.compare_paths_screen import ComparePathsScreen
from gui.widgets.sensor_screen import SensorScreen
from gui.widgets.macro_screen import MacroScreen
from gui.widgets.home_screen import HomeScreen
from gui.widgets.shaftsync_screen import ShaftSyncScreen   # NEW IMPORT


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚘 PathVision")
        self.setMinimumSize(800, 600)

        # Stacked widget to hold all screens
        self.stack = QStackedWidget()

        # Screens dictionary for easy switching
        self.screens = {}
        self.screens['home'] = QWidget()  # Home screen container
        self.screens['add'] = AddPathScreen(self.go_home)
        self.screens['existing'] = ExistingPathsScreen(self.go_home)
        self.screens['compare'] = ComparePathsScreen(self.go_home)
        self.screens['sensor'] = SensorScreen()
        self.screens['macro'] = MacroScreen(self.go_home)
        self.screens['shaftsync'] = ShaftSyncScreen(self.go_home)  # NEW SCREEN

        # Connect sensor back button
        self.screens['sensor'].back_button.clicked.connect(self.go_home)

        # Initialize Home UI
        self.init_home_ui()

        # Add all screens to stacked widget
        for screen in self.screens.values():
            self.stack.addWidget(screen)

        # Set main layout
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        # Show home screen initially
        self.switch_screen('home')

    # ---------- Home UI ----------
    def init_home_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        button_style = """
            QPushButton {
                font-size: 16px;
                padding: 10px 20px;
                min-width: 200px;
                max-width: 300px;
            }
        """

        # Buttons
        btn_add = QPushButton("➕ Add New Path")
        btn_add.setStyleSheet(button_style)
        btn_add.clicked.connect(lambda: self.switch_screen('add'))

        btn_existing = QPushButton("📁 View Existing Paths")
        btn_existing.setStyleSheet(button_style)
        btn_existing.clicked.connect(lambda: self.switch_screen('existing'))

        btn_compare = QPushButton("🔍 Compare Paths")
        btn_compare.setStyleSheet(button_style)
        btn_compare.clicked.connect(lambda: self.switch_screen('compare'))

        btn_sensor = QPushButton("📡 View Sensor Data")
        btn_sensor.setStyleSheet(button_style)
        btn_sensor.clicked.connect(lambda: self.switch_screen('sensor'))

        btn_macro = QPushButton("⚙️ Generate Macro")
        btn_macro.setStyleSheet(button_style)
        btn_macro.clicked.connect(lambda: self.switch_screen('macro'))

        btn_shaftsync = QPushButton("🔄 ShaftSync (Encoders)")  # NEW BUTTON
        btn_shaftsync.setStyleSheet(button_style)
        btn_shaftsync.clicked.connect(lambda: self.switch_screen('shaftsync'))

        # Add buttons centered
        for btn in [btn_add, btn_existing, btn_compare, btn_sensor, btn_macro, btn_shaftsync]:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            layout.addWidget(btn, alignment=Qt.AlignHCenter)

        self.screens['home'].setLayout(layout)

    # ---------- Navigation ----------
    def switch_screen(self, key: str):
        """Switch to the screen by key."""
        if key in self.screens:
            screen = self.screens[key]
            # Call refresh() if available
            if hasattr(screen, 'refresh'):
                screen.refresh()
            self.stack.setCurrentWidget(screen)

    def go_home(self):
        """Shortcut to return to Home screen."""
        self.switch_screen('home')
