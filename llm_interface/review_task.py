"""
Enhanced review task implementation with C++ performance integration.

This module provides thread-safe task execution for LLM reviews with
optimized streaming and buffering using C++ backend when available.
"""

import logging
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QTimer
from PyQt6.QtWidgets import QApplication

from llm_interface.qwen_runner import stream_code_review, stream_follow_up, LLMError
from config.app_config import config

logger = logging.getLogger(__name__)

try:
    import core_performance
    HAS_CPP_BACKEND = True
except ImportError:
    logger.warning("C++ performance module not available for streaming optimization")
    HAS_CPP_BACKEND = False


class ReviewWorkerSignals(QObject):
    """Signals for communicating with the main thread."""
    
    # Emitted when new content is available for display
    content_ready = pyqtSignal(str)
    
    # Emitted when streaming is complete
    finished = pyqtSignal()
    
    # Emitted when an error occurs
    error = pyqtSignal(str)
    
    # Emitted with progress information
    progress = pyqtSignal(str)


class BaseReviewTask(QRunnable):
    """
    Base class for review tasks with enhanced streaming capabilities.
    """
    
    def __init__(self):
        super().__init__()
        self.signals = ReviewWorkerSignals()
        self._is_cancelled = False
        self._streamer: Optional[object] = None
        
        # Initialize C++ streamer if available
        if HAS_CPP_BACKEND:
            self._setup_cpp_streamer()
        else:
            self._setup_python_fallback()
    
    def _setup_cpp_streamer(self):
        """Setup the C++ text streamer for optimal performance."""
        try:
            self._streamer = core_performance.AdaptiveTextStreamer(
                buffer_size=config.buffer_size,
                flush_interval_ms=config.flush_interval_ms
            )
            
            # Set up callback to emit content to main thread
            def content_callback(content: str):
                if not self._is_cancelled:
                    # Use QApplication.postEvent for thread-safe signal emission
                    QApplication.postEvent(
                        self.signals,
                        ContentReadyEvent(content)
                    )
            
            self._streamer.set_update_callback(content_callback)
            logger.debug("C++ streamer initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize C++ streamer: {e}. Using Python fallback.")
            self._setup_python_fallback()
    
    def _setup_python_fallback(self):
        """Setup Python fallback for token streaming."""
        self._buffer = []
        self._buffer_size = config.buffer_size
        logger.debug("Using Python fallback for token streaming")
    
    def _add_token(self, token: str):
        """Add a token to the stream buffer."""
        if self._is_cancelled:
            return
        
        if HAS_CPP_BACKEND and self._streamer:
            self._streamer.add_token(token)
        else:
            # Python fallback
            self._buffer.append(token)
            if len(self._buffer) >= self._buffer_size:
                self._flush_python_buffer()
    
    def _flush_python_buffer(self):
        """Flush the Python token buffer."""
        if self._buffer:
            content = ''.join(self._buffer)
            self._buffer.clear()
            self.signals.content_ready.emit(content)
    
    def _start_streaming(self):
        """Start the streaming process."""
        if HAS_CPP_BACKEND and self._streamer:
            self._streamer.start_streaming()
    
    def _stop_streaming(self):
        """Stop the streaming process and flush remaining content."""
        if HAS_CPP_BACKEND and self._streamer:
            self._streamer.stop_streaming()
        else:
            # Flush any remaining tokens in Python fallback
            self._flush_python_buffer()
    
    def cancel(self):
        """Cancel the current task."""
        self._is_cancelled = True
        if HAS_CPP_BACKEND and self._streamer:
            self._streamer.stop_streaming()
        logger.info(f"Task {self.__class__.__name__} cancelled")
    
    def run(self):
        """Execute the task. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement run method")


class ReviewTask(BaseReviewTask):
    """Task for performing code reviews."""
    
    def __init__(self, code: str):
        super().__init__()
        self.code = code
        logger.info(f"Created ReviewTask for {len(code)} characters of code")
    
    def run(self):
        """Execute the code review task."""
        try:
            if not self.code or not self.code.strip():
                self.signals.error.emit("No code provided for review")
                return
            
            self.signals.progress.emit("Starting code review...")
            self._start_streaming()
            
            # Stream tokens from LLM
            token_count = 0
            for token in stream_code_review(self.code):
                if self._is_cancelled:
                    logger.info("ReviewTask cancelled during execution")
                    return
                
                if token.startswith("[ERROR]"):
                    self.signals.error.emit(token)
                    return
                
                self._add_token(token)
                token_count += 1
                
                # Periodic progress updates
                if token_count % 50 == 0:
                    self.signals.progress.emit(f"Received {token_count} tokens...")
            
            # Ensure all content is flushed
            self._stop_streaming()
            
            self.signals.progress.emit("Code review completed")
            self.signals.finished.emit()
            logger.info(f"ReviewTask completed successfully with {token_count} tokens")
            
        except LLMError as e:
            logger.error(f"LLM error in ReviewTask: {e}")
            self.signals.error.emit(f"LLM Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in ReviewTask: {e}")
            self.signals.error.emit(f"Unexpected error: {e}")
        finally:
            self._stop_streaming()


class FollowUpTask(BaseReviewTask):
    """Task for handling follow-up questions."""
    
    def __init__(self, original_review: str, question: str):
        super().__init__()
        self.original_review = original_review
        self.question = question
        logger.info(f"Created FollowUpTask for question: {question[:50]}...")
    
    def run(self):
        """Execute the follow-up question task."""
        try:
            if not self.question or not self.question.strip():
                self.signals.error.emit("No question provided for follow-up")
                return
            
            self.signals.progress.emit("Processing follow-up question...")
            self._start_streaming()
            
            # Add separator for follow-up content
            self._add_token(f"\n\n---\n\n**Follow-up:** {self.question}\n\n")
            
            # Stream tokens from LLM
            token_count = 0
            for token in stream_follow_up(self.original_review, self.question):
                if self._is_cancelled:
                    logger.info("FollowUpTask cancelled during execution")
                    return
                
                if token.startswith("[ERROR]"):
                    self.signals.error.emit(token)
                    return
                
                self._add_token(token)
                token_count += 1
                
                # Periodic progress updates
                if token_count % 30 == 0:
                    self.signals.progress.emit(f"Processing response... ({token_count} tokens)")
            
            # Ensure all content is flushed
            self._stop_streaming()
            
            self.signals.progress.emit("Follow-up completed")
            self.signals.finished.emit()
            logger.info(f"FollowUpTask completed successfully with {token_count} tokens")
            
        except LLMError as e:
            logger.error(f"LLM error in FollowUpTask: {e}")
            self.signals.error.emit(f"LLM Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in FollowUpTask: {e}")
            self.signals.error.emit(f"Unexpected error: {e}")
        finally:
            self._stop_streaming()


class TaskManager:
    """
    Manager for coordinating multiple review tasks.
    """
    
    def __init__(self):
        self.current_task: Optional[BaseReviewTask] = None
        self.task_history = []
    
    def start_review(self, code: str, signals_target) -> ReviewTask:
        """Start a new review task."""
        self._cancel_current_task()
        
        task = ReviewTask(code)
        self._connect_signals(task, signals_target)
        self.current_task = task
        self.task_history.append(('review', len(code)))
        
        return task
    
    def start_followup(self, original_review: str, question: str, signals_target) -> FollowUpTask:
        """Start a new follow-up task."""
        self._cancel_current_task()
        
        task = FollowUpTask(original_review, question)
        self._connect_signals(task, signals_target)
        self.current_task = task
        self.task_history.append(('followup', len(question)))
        
        return task
    
    def _cancel_current_task(self):
        """Cancel the currently running task if any."""
        if self.current_task:
            self.current_task.cancel()
            self.current_task = None
    
    def _connect_signals(self, task: BaseReviewTask, signals_target):
        """Connect task signals to the target object."""
        task.signals.content_ready.connect(signals_target.append_content)
        task.signals.finished.connect(signals_target.task_finished)
        task.signals.error.connect(signals_target.display_error)
        task.signals.progress.connect(signals_target.update_progress)
    
    def get_stats(self) -> dict:
        """Get statistics about task execution."""
        return {
            'total_tasks': len(self.task_history),
            'reviews': sum(1 for task_type, _ in self.task_history if task_type == 'review'),
            'followups': sum(1 for task_type, _ in self.task_history if task_type == 'followup'),
            'has_current_task': self.current_task is not None
        }


# Custom event for thread-safe content updates
from PyQt6.QtCore import QEvent

class ContentReadyEvent(QEvent):
    """Custom event for content ready notifications."""
    
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, content: str):
        super().__init__(self.EVENT_TYPE)
        self.content = content