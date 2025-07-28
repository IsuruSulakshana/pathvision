from PyQt5.QtWidgets import QApplication
import sys
from gui.add_path import AddPathScreen

def launch_app():
    app = QApplication(sys.argv)
    window = AddPathScreen()
    window.show()
    sys.exit(app.exec_())
