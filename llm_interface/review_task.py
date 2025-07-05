# llm_interface/review_task.py

from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from llm_interface.qwen_runner import run_code_review

class ReviewWorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)


class ReviewTask(QRunnable):
    def __init__(self, code: str):
        super().__init__()
        self.code = code
        self.signals = ReviewWorkerSignals()

    def run(self):
        try:
            response = run_code_review(self.code)
            self.signals.finished.emit(response)
        except Exception as e:
            self.signals.error.emit(str(e))
