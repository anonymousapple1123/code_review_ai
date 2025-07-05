from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QTextBrowser, QTextEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QTextCursor
import os

from gui.file_loader import load_file_content
from llm_interface.review_task import ReviewTask, FollowUpTask


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.full_response_text = ""
        self.threadpool = QThreadPool()
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        self.setWindowTitle("Local Code Review App")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Top button bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.select_file_button = QPushButton("📂")
        self.select_file_button.setToolTip("Select Python File")
        self.select_file_button.clicked.connect(self.select_file)

        self.review_button = QPushButton("🔍")
        self.review_button.setToolTip("Review Code")
        self.review_button.clicked.connect(self.review_code)
        self.review_button.setDisabled(True)

        self.run_button = QPushButton("▶️")
        self.run_button.setToolTip("Run Code in Sandbox")
        self.run_button.clicked.connect(self.run_code)
        self.run_button.setDisabled(True)

        self.theme_button = QPushButton("🌙")
        self.theme_button.setToolTip("Toggle Dark/Light Mode")
        self.theme_button.clicked.connect(self.toggle_theme)

        for btn in [self.select_file_button, self.review_button, self.run_button, self.theme_button]:
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(
                "QPushButton { border-radius: 20px; background-color: #0078D7; color: white; }"
                "QPushButton:hover { background-color: #005fa3; }"
            )

        top_bar.addWidget(self.select_file_button)
        top_bar.addWidget(self.review_button)
        top_bar.addWidget(self.run_button)
        top_bar.addStretch()
        top_bar.addWidget(self.theme_button)

        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: gray;")
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray; font-style: italic;")

        self.review_output = QTextBrowser()
        self.review_output.setPlaceholderText("Your code review will appear here...")
        self.review_output.setMinimumHeight(790)  # or any height that suits your screen
        self.review_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

       

        followup_container = QHBoxLayout()
        followup_container.setSpacing(10)

        self.followup_box = QTextEdit()
        self.followup_box.setPlaceholderText("Ask a follow-up question...")
        self.followup_box.setDisabled(True)
        self.followup_box.setFixedHeight(50)
        self.followup_box.setStyleSheet(
            "QTextEdit { border: 1px solid #ccc; border-radius: 10px; padding: 8px; font-size: 14px; }"
        )

        self.ask_button = QPushButton("➤")
        self.ask_button.setDisabled(True)
        self.ask_button.setFixedSize(40, 40)
        self.ask_button.clicked.connect(self.ask_followup)
        self.ask_button.setStyleSheet(
            "QPushButton { border-radius: 20px; background-color: #0078D7; color: white; }"
            "QPushButton:hover { background-color: #005fa3; }"
        )

        followup_container.addWidget(self.followup_box)
        followup_container.addWidget(self.ask_button)

        main_layout.addLayout(top_bar)
        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.review_output)
        main_layout.addLayout(followup_container)
        main_layout.addStretch()

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    def toggle_theme(self):
        if self.current_theme == "light":
            self.setStyleSheet(
                """
                QWidget { background-color: #121212; color: #e0e0e0; }
                QPushButton { background-color: #333; color: #eee; border-radius: 20px; }
                QPushButton:hover { background-color: #444; }
                QTextBrowser {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                    border: 1px solid #444;
                    border-radius: 10px;
                    padding: 10px;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                    border: 1px solid #444;
                    border-radius: 10px;
                    padding: 8px;
                }
                """
            )
            self.current_theme = "dark"
        else:
            self.setStyleSheet(
                """
                QWidget { background-color: #ffffff; color: #000000; }
                QPushButton { background-color: #e0e0e0; color: #000000; border-radius: 20px; }
                QPushButton:hover { background-color: #d0d0d0; }
                QTextBrowser {
                    background-color: #1e1e1e;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    padding: 10px;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    padding: 8px;
                }
                """
            )
            self.current_theme = "light"



    def select_file(self):
        dialog = QFileDialog(self)
        dialog.setNameFilter("Python Files (*.py)")
        if dialog.exec():
            files = dialog.selectedFiles()
            if files:
                self.file_label.setText(files[0])
                self.review_button.setEnabled(True)
                self.run_button.setEnabled(True)

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

        # Reset buffer with header
        self.full_response_text = f"# Review: {os.path.basename(file_path)}\n\n"
        self.review_output.clear()
        self.status_label.setText("⏳ Reviewing code...")
        self.review_button.setEnabled(False)
        self.select_file_button.setEnabled(False)
        self.ask_button.setEnabled(False)
        self.followup_box.setEnabled(False)

        task = ReviewTask(code)
        task.signals.streamed.connect(self.append_token)
        task.signals.finished.connect(self.review_done)
        task.signals.error.connect(self.display_error)
        self.threadpool.start(task)

    def append_token(self, token: str):
        scroll_bar = self.review_output.verticalScrollBar()
        at_bottom = scroll_bar.value() == scroll_bar.maximum()
        self.full_response_text += token
        self.review_output.setStyleSheet("QTextBrowser { color: #f0f0f0; }")

        self.review_output.setMarkdown(self.full_response_text)
        if at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())

    def review_done(self):
        self.status_label.setText("✅ Review complete.")
        self.review_button.setEnabled(True)
        self.select_file_button.setEnabled(True)
        self.ask_button.setEnabled(True)
        self.followup_box.setEnabled(True)

    def ask_followup(self):
        question = self.followup_box.toPlainText().strip()
        if not question:
            QMessageBox.warning(self, "Empty Question", "Please enter a follow-up question.")
            return

        self.status_label.setText("🤔 Asking follow-up...")
        self.ask_button.setEnabled(False)
        self.followup_box.setEnabled(False)

        task = FollowUpTask(self.full_response_text, question)
        task.signals.streamed.connect(self.append_followup_token)
        task.signals.finished.connect(self.followup_done)
        task.signals.error.connect(self.display_error)
        self.threadpool.start(task)

    def append_followup_token(self, token: str):
        scroll_bar = self.review_output.verticalScrollBar()
        at_bottom = scroll_bar.value() == scroll_bar.maximum()
        self.full_response_text += token
        self.review_output.setMarkdown(self.full_response_text)
        if at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())

    def followup_done(self):
        self.status_label.setText("✅ Follow-up complete.")
        self.ask_button.setEnabled(True)
        self.followup_box.setEnabled(True)
        self.followup_box.clear()

    def run_code(self):
        # Placeholder for sandboxed execution
        QMessageBox.information(self, "Run Code", "Sandboxed execution coming soon.")

   
    def display_error(self, error: str):
        QMessageBox.critical(self, "LLM Error", error)
        self.status_label.setText("❌ Error occurred.")
        self.review_button.setEnabled(True)
        self.select_file_button.setEnabled(True)
        self.ask_button.setEnabled(True)
        self.followup_box.setEnabled(True)
