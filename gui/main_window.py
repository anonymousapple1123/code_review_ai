"""
Enhanced main window with improved performance and user experience.

This module provides the main GUI interface with optimized text rendering,
better error handling, and integration with C++ performance modules.
"""

import os
import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QFileDialog, QTextBrowser, QTextEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, 
    QSizePolicy, QStatusBar, QProgressBar, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QThreadPool, QTimer, QThread
from PyQt6.QtGui import QTextCursor, QFont, QTextDocument, QPalette, QColor

from gui.file_loader import FileLoader, FileLoadError
from llm_interface.review_task import TaskManager
from config.app_config import config

logger = logging.getLogger(__name__)


class EnhancedTextDisplay(QTextBrowser):
    """
    Enhanced text display widget with optimized rendering for streaming content.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_display()
        self._setup_performance_optimizations()
    
    def _setup_display(self):
        """Setup the text display widget."""
        # Set font and styling
        font = QFont("Consolas", 11)  # Monospace font for code
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Configure text behavior
        self.setOpenExternalLinks(False)  # Handle links manually
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        # Set placeholder text
        self.setPlaceholderText(
            "Your code review will appear here...\n\n"
            "• Select a Python file using the folder button\n"
            "• Click the review button to start analysis\n"
            "• Ask follow-up questions in the text box below"
        )
    
    def _setup_performance_optimizations(self):
        """Setup performance optimizations for text rendering."""
        # Limit document size to prevent memory issues
        self.document().setMaximumBlockCount(10000)
        
        # Optimize rendering
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    
    def append_content_optimized(self, content: str):
        """
        Append content with optimized rendering to prevent UI freezing.
        """
        # Check if we're at the bottom before adding content
        scrollbar = self.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # Use QTextCursor for efficient appending
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(content)
        
        # Auto-scroll if we were at the bottom
        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
    
    def set_content_with_markdown(self, content: str):
        """Set content with markdown rendering (use sparingly)."""
        self.setMarkdown(content)


class MainWindow(QMainWindow):
    """Enhanced main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.file_loader = FileLoader()
        self.task_manager = TaskManager()
        self.threadpool = QThreadPool()
        
        # UI state
        self.current_theme = config.ui_theme
        self.selected_file_path = ""
        self.full_response_text = ""
        
        # Performance monitoring
        self._last_update_time = 0
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._delayed_markdown_update)
        
        # Setup UI
        self._init_ui()
        self._apply_theme()
        self._setup_window()
        
        logger.info("MainWindow initialized successfully")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Create UI sections
        self._create_toolbar()
        self._create_file_info_section()
        self._create_main_content()
        self._create_input_section()
        self._create_status_bar()
        
        # Add sections to main layout
        main_layout.addLayout(self.toolbar_layout)
        main_layout.addLayout(self.file_info_layout)
        main_layout.addWidget(self.content_splitter, 1)  # Takes remaining space
        main_layout.addLayout(self.input_layout)
    
    def _create_toolbar(self):
        """Create the main toolbar with action buttons."""
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setSpacing(8)
        
        # File selection button
        self.select_file_btn = QPushButton("📂 Select File")
        self.select_file_btn.setToolTip("Select a Python file for review")
        self.select_file_btn.clicked.connect(self._select_file)
        
        # Review button
        self.review_btn = QPushButton("🔍 Review Code")
        self.review_btn.setToolTip("Start code review")
        self.review_btn.clicked.connect(self._review_code)
        self.review_btn.setEnabled(False)
        
        # Clear button
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.setToolTip("Clear the review output")
        self.clear_btn.clicked.connect(self._clear_output)
        
        # Theme toggle button
        self.theme_btn = QPushButton("🌙" if self.current_theme == "light" else "☀️")
        self.theme_btn.setToolTip("Toggle dark/light theme")
        self.theme_btn.clicked.connect(self._toggle_theme)
        
        # Connection test button
        self.test_connection_btn = QPushButton("🔗 Test LLM")
        self.test_connection_btn.setToolTip("Test connection to LLM service")
        self.test_connection_btn.clicked.connect(self._test_llm_connection)
        
        # Add buttons to toolbar
        for btn in [self.select_file_btn, self.review_btn, self.clear_btn]:
            btn.setMinimumHeight(35)
            self.toolbar_layout.addWidget(btn)
        
        self.toolbar_layout.addStretch()  # Push remaining buttons to right
        
        for btn in [self.test_connection_btn, self.theme_btn]:
            btn.setFixedSize(35, 35)
            self.toolbar_layout.addWidget(btn)
    
    def _create_file_info_section(self):
        """Create the file information display section."""
        self.file_info_layout = QHBoxLayout()
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: gray; font-style: italic;")
        
        self.file_size_label = QLabel("")
        self.file_size_label.setStyleSheet("color: gray; font-size: 11px;")
        
        self.file_info_layout.addWidget(QLabel("📄 File:"))
        self.file_info_layout.addWidget(self.file_label)
        self.file_info_layout.addWidget(self.file_size_label)
        self.file_info_layout.addStretch()
    
    def _create_main_content(self):
        """Create the main content area with splitter."""
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Review output display
        self.review_output = EnhancedTextDisplay()
        self.review_output.setMinimumHeight(500)
        
        # Optional side panel for additional info (collapsed by default)
        self.side_panel = QFrame()
        self.side_panel.setMaximumWidth(0)  # Hidden initially
        
        self.content_splitter.addWidget(self.review_output)
        self.content_splitter.addWidget(self.side_panel)
        self.content_splitter.setSizes([1000, 0])  # Full width to main panel
    
    def _create_input_section(self):
        """Create the follow-up question input section."""
        self.input_layout = QHBoxLayout()
        self.input_layout.setSpacing(10)
        
        # Follow-up question input
        self.followup_input = QTextEdit()
        self.followup_input.setPlaceholderText("Ask a follow-up question about the code...")
        self.followup_input.setMaximumHeight(60)
        self.followup_input.setEnabled(False)
        
        # Ask button
        self.ask_btn = QPushButton("➤ Ask")
        self.ask_btn.setFixedSize(60, 50)
        self.ask_btn.setEnabled(False)
        self.ask_btn.clicked.connect(self._ask_followup)
        
        self.input_layout.addWidget(self.followup_input)
        self.input_layout.addWidget(self.ask_btn)
    
    def _create_status_bar(self):
        """Create the status bar with progress indication."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar for long operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Connection status
        self.connection_status = QLabel("LLM: Unknown")
        self.status_bar.addPermanentWidget(self.connection_status)
    
    def _setup_window(self):
        """Setup main window properties."""
        self.setWindowTitle("Code Review Assistant - Enhanced Edition")
        
        # Set window size from config
        width, height = config.window_size
        self.resize(width, height)
        
        # Center window on screen
        self._center_window()
    
    def _center_window(self):
        """Center the window on the screen."""
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        window = self.geometry()
        self.move(
            (screen.width() - window.width()) // 2,
            (screen.height() - window.height()) // 2
        )
    
    def _apply_theme(self):
        """Apply the current theme to the application."""
        if self.current_theme == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_dark_theme(self):
        """Apply dark theme styling."""
        dark_stylesheet = """
            QMainWindow { 
                background-color: #2b2b2b; 
                color: #ffffff; 
            }
            QTextBrowser, QTextEdit { 
                background-color: #1e1e1e; 
                color: #f0f0f0; 
                border: 1px solid #555; 
                border-radius: 8px; 
                padding: 10px; 
            }
            QPushButton { 
                background-color: #404040; 
                color: #ffffff; 
                border: 1px solid #666; 
                border-radius: 6px; 
                padding: 8px 16px; 
            }
            QPushButton:hover { 
                background-color: #505050; 
            }
            QPushButton:pressed { 
                background-color: #353535; 
            }
            QPushButton:disabled { 
                background-color: #2a2a2a; 
                color: #666; 
            }
            QLabel { 
                color: #ffffff; 
            }
            QStatusBar { 
                background-color: #333; 
                color: #fff; 
            }
        """
        self.setStyleSheet(dark_stylesheet)
    
    def _apply_light_theme(self):
        """Apply light theme styling."""
        light_stylesheet = """
            QMainWindow { 
                background-color: #ffffff; 
                color: #000000; 
            }
            QTextBrowser, QTextEdit { 
                background-color: #ffffff; 
                color: #000000; 
                border: 1px solid #ccc; 
                border-radius: 8px; 
                padding: 10px; 
            }
            QPushButton { 
                background-color: #f0f0f0; 
                color: #000000; 
                border: 1px solid #ccc; 
                border-radius: 6px; 
                padding: 8px 16px; 
            }
            QPushButton:hover { 
                background-color: #e0e0e0; 
            }
            QPushButton:pressed { 
                background-color: #d0d0d0; 
            }
            QPushButton:disabled { 
                background-color: #f5f5f5; 
                color: #999; 
            }
        """
        self.setStyleSheet(light_stylesheet)
    
    # Event handlers
    def _select_file(self):
        """Handle file selection."""
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setNameFilter("Python Files (*.py)")
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            
            if file_dialog.exec():
                files = file_dialog.selectedFiles()
                if files:
                    self._load_selected_file(files[0])
        except Exception as e:
            logger.error(f"Error in file selection: {e}")
            QMessageBox.critical(self, "File Selection Error", f"Failed to select file: {e}")
    
    def _load_selected_file(self, file_path: str):
        """Load and display information about the selected file."""
        try:
            file_info = self.file_loader.get_file_info(file_path)
            
            if not file_info.get('is_valid_python', False):
                QMessageBox.warning(self, "Invalid File", "Please select a valid Python file.")
                return
            
            self.selected_file_path = file_path
            self.file_label.setText(file_info['name'])
            self.file_size_label.setText(f"({file_info['size']} bytes)")
            
            # Enable review button
            self.review_btn.setEnabled(True)
            
            self.status_label.setText(f"File loaded: {file_info['name']}")
            logger.info(f"File selected: {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading file info: {e}")
            QMessageBox.critical(self, "File Load Error", f"Failed to load file information: {e}")
    
    def _review_code(self):
        """Start the code review process."""
        if not self.selected_file_path:
            QMessageBox.warning(self, "No File", "Please select a Python file first.")
            return
        
        try:
            # Load file content
            code = self.file_loader.load(self.selected_file_path)
            
            # Clear previous output
            self._clear_output()
            
            # Start review task
            self._start_review_task(code)
            
        except FileLoadError as e:
            logger.error(f"File load error: {e}")
            QMessageBox.critical(self, "File Load Error", str(e))
        except Exception as e:
            logger.error(f"Unexpected error starting review: {e}")
            QMessageBox.critical(self, "Review Error", f"Failed to start review: {e}")
    
    def _start_review_task(self, code: str):
        """Start the review task with proper UI state management."""
        # Set UI state for processing
        self._set_processing_state(True, "Analyzing code...")
        
        # Reset response text
        filename = os.path.basename(self.selected_file_path)
        self.full_response_text = f"# Code Review: {filename}\n\n"
        
        # Start task
        task = self.task_manager.start_review(code, self)
        self.threadpool.start(task)
        
        logger.info(f"Started review task for {filename}")
    
    def _ask_followup(self):
        """Handle follow-up question."""
        question = self.followup_input.toPlainText().strip()
        if not question:
            QMessageBox.warning(self, "Empty Question", "Please enter a follow-up question.")
            return
        
        try:
            # Set UI state
            self._set_processing_state(True, "Processing follow-up question...")
            
            # Start follow-up task
            task = self.task_manager.start_followup(self.full_response_text, question, self)
            self.threadpool.start(task)
            
            # Clear input
            self.followup_input.clear()
            
            logger.info(f"Started follow-up task: {question[:50]}...")
            
        except Exception as e:
            logger.error(f"Error starting follow-up task: {e}")
            QMessageBox.critical(self, "Follow-up Error", f"Failed to process question: {e}")
    
    def _clear_output(self):
        """Clear the review output."""
        self.review_output.clear()
        self.full_response_text = ""
        logger.debug("Review output cleared")
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._apply_theme()
        
        # Update theme button
        self.theme_btn.setText("☀️" if self.current_theme == "dark" else "🌙")
        
        # Save theme preference
        config.set('ui_theme', self.current_theme)
        config.save()
        
        logger.info(f"Theme changed to: {self.current_theme}")
    
    def _test_llm_connection(self):
        """Test connection to the LLM service."""
        from llm_interface.qwen_runner import llm_client
        
        self.status_label.setText("Testing LLM connection...")
        
        try:
            if llm_client.test_connection():
                self.connection_status.setText("LLM: ✓ Connected")
                self.connection_status.setStyleSheet("color: green;")
                QMessageBox.information(self, "Connection Test", "Successfully connected to LLM service!")
            else:
                self.connection_status.setText("LLM: ✗ Failed")
                self.connection_status.setStyleSheet("color: red;")
                QMessageBox.warning(self, "Connection Test", "Failed to connect to LLM service.")
        except Exception as e:
            self.connection_status.setText("LLM: ✗ Error")
            self.connection_status.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Connection Test", f"Connection test error: {e}")
        
        self.status_label.setText("Ready")
    
    def _set_processing_state(self, is_processing: bool, status_text: str = ""):
        """Set UI state for processing operations."""
        # Enable/disable buttons
        self.select_file_btn.setEnabled(not is_processing)
        self.review_btn.setEnabled(not is_processing and bool(self.selected_file_path))
        self.ask_btn.setEnabled(not is_processing and bool(self.full_response_text))
        self.followup_input.setEnabled(not is_processing and bool(self.full_response_text))
        
        # Update status
        if status_text:
            self.status_label.setText(status_text)
        
        # Show/hide progress bar
        self.progress_bar.setVisible(is_processing)
        if is_processing:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
    
    def _delayed_markdown_update(self):
        """Update markdown display with delay to prevent UI freezing."""
        if self.full_response_text:
            self.review_output.set_content_with_markdown(self.full_response_text)
    
    # Task callback methods
    def append_content(self, content: str):
        """Callback for appending content from tasks."""
        self.full_response_text += content
        
        # Use optimized appending instead of full markdown update
        self.review_output.append_content_optimized(content)
        
        # Schedule delayed markdown update for final formatting
        self._update_timer.start(500)  # Update markdown after 500ms delay
    
    def task_finished(self):
        """Callback for when a task finishes."""
        self._set_processing_state(False, "Ready")
        
        # Enable follow-up input if we have content
        if self.full_response_text:
            self.followup_input.setEnabled(True)
            self.ask_btn.setEnabled(True)
        
        # Final markdown update
        self._update_timer.stop()
        self.review_output.set_content_with_markdown(self.full_response_text)
        
        logger.info("Task completed successfully")
    
    def display_error(self, error_message: str):
        """Callback for displaying errors from tasks."""
        self._set_processing_state(False, "Error occurred")
        
        QMessageBox.critical(self, "Task Error", error_message)
        logger.error(f"Task error: {error_message}")
    
    def update_progress(self, progress_text: str):
        """Callback for updating progress information."""
        self.status_label.setText(progress_text)
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Cancel any running tasks
        if self.task_manager.current_task:
            self.task_manager.current_task.cancel()
        
        # Save window geometry
        config.set('window_width', self.width())
        config.set('window_height', self.height())
        config.save()
        
        logger.info("Application closing")
        event.accept()