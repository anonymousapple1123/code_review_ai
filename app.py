# app.py

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # Optional: Set application name/organization for future settings or themes
    app.setApplicationName("Code Reviewer AI")
    app.setOrganizationName("LocalLLM")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
