from PyQt6.QtWidgets import QFileDialog, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel, QLineEdit, QMessageBox
from PyQt6.QtCore import Qt, QThreadPool
from gui.file_loader import load_file_content
from llm_interface.review_task import ReviewTask

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Code Review App")
        self.setMinimumSize(700, 500)
        self.threadpool = QThreadPool()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.file_label = QLabel("No file selected")

        # ⬇️ Add this
        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.select_file)

        self.review_button = QPushButton("Review Code")
        self.review_button.clicked.connect(self.review_code)

        self.review_output = QTextEdit()
        self.review_output.setReadOnly(True)

        # ⬇️ Add select_file_button to layout
        layout.addWidget(self.file_label)
        layout.addWidget(self.select_file_button)
        layout.addWidget(self.review_button)
        layout.addWidget(self.review_output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def review_code(self):
        file_path = self.file_label.text()
        if file_path == "No file selected":
            QMessageBox.warning(self, "No File", "Please select a Python file first.")
            return

        try:
            code = load_file_content(file_path)
        except Exception as e:
            QMessageBox.critical(self, "File Error", str(e))
            return

        # Clear UI and show loading
        self.review_output.setText("⏳ Running code review... Please wait.")

        # Start threaded review
        task = ReviewTask(code)
        task.signals.finished.connect(self.display_result)
        task.signals.error.connect(self.display_error)
        self.threadpool.start(task)

    def display_result(self, result: str):
        self.review_output.setText(result)

    def display_error(self, error: str):
        self.review_output.setText(f"❌ Error: {error}")

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Python Files (*.py)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.file_label.setText(selected_files[0])

