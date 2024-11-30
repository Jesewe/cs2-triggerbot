import sys
from PyQt6.QtWidgets import QApplication
from classes.logger import Logger
from classes.main_window import MainWindow

if __name__ == "__main__":
    Logger.setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())