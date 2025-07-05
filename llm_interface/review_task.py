# llm_interface/review_task.py

from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from llm_interface.qwen_runner import stream_code_review, stream_follow_up


class ReviewWorkerSignals(QObject):
    streamed = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)


class ReviewTask(QRunnable):
    def __init__(self, code: str):
        super().__init__()
        self.code = code
        self.signals = ReviewWorkerSignals()

    def run(self):
        try:
            for chunk in stream_code_review(self.code):
                if chunk.startswith("[ERROR]"):
                    self.signals.error.emit(chunk)
                    return
                self.signals.streamed.emit(chunk)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))


class FollowUpTask(QRunnable):
    def __init__(self, original_review: str, question: str):
        super().__init__()
        self.original_review = original_review
        self.question = question
        self.signals = ReviewWorkerSignals()

    def run(self):
        try:
            for chunk in stream_follow_up(self.original_review, self.question):
                if chunk.startswith("[ERROR]"):
                    self.signals.error.emit(chunk)
                    return
                self.signals.streamed.emit(chunk)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))
