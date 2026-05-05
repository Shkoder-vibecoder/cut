import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from db.migrations import init_db


def main():
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("ИС Раскрой")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()