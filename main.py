from PyQt5.QtWidgets import QApplication
from gui.home import AppWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())
