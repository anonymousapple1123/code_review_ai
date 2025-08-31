#!/usr/bin/env python3
"""
Enhanced Code Review Application - Main Entry Point

This is the main entry point for the Code Review Assistant application.
It initializes the Qt application, sets up logging, and launches the main window.
"""

import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add the project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from gui.main_window import MainWindow
from config.app_config import config

# Setup logging
logger = logging.getLogger(__name__)


def setup_application():
    """Setup the Qt application with proper configuration."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Code Review Assistant")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("LocalLLM")
    app.setOrganizationDomain("github.com/yourname/code-review-app")
    
    # Set application icon if available
    icon_path = PROJECT_ROOT / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Setup application style
    app.setStyle('Fusion')  # Modern cross-platform style
    
    return app


def check_dependencies():
    """Check for required dependencies and display warnings if missing."""
    missing_deps = []
    warnings = []
    
    # Check for C++ performance module
    try:
        import core_performance
        logger.info("C++ performance module loaded successfully")
    except ImportError:
        warnings.append(
            "C++ performance module not available. "
            "Run 'python setup.py build_ext --inplace' to build it for better performance."
        )
    
    # Check for Ollama connection
    try:
        import requests
        response = requests.get(config.ollama_api_url.replace('/api/chat', '/api/tags'), timeout=2)
        if response.status_code == 200:
            logger.info("Ollama service is available")
        else:
            warnings.append("Ollama service is not responding properly")
    except Exception:
        warnings.append(
            "Could not connect to Ollama service. "
            "Please ensure Ollama is installed and running with 'ollama run qwen2.5-coder'"
        )
    
    return missing_deps, warnings


def show_startup_info(warnings):
    """Show startup information and warnings to the user."""
    if warnings:
        message = "Code Review Assistant is starting with the following notices:\n\n"
        message += "\n".join(f"• {warning}" for warning in warnings)
        message += "\n\nThe application will still work, but some features may be limited."
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Startup Information")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow Ctrl+C to work normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Show error dialog to user
    error_msg = f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}"
    QMessageBox.critical(None, "Critical Error", error_msg)


def setup_error_handling():
    """Setup global error handling."""
    sys.excepthook = handle_exception


def main():
    """Main application entry point."""
    # Setup error handling first
    setup_error_handling()
    
    logger.info("Starting Code Review Assistant v2.0.0")
    
    try:
        # Create Qt application
        app = setup_application()
        
        # Check dependencies
        missing_deps, warnings = check_dependencies()
        
        if missing_deps:
            error_msg = "Missing required dependencies:\n\n"
            error_msg += "\n".join(f"• {dep}" for dep in missing_deps)
            error_msg += "\n\nPlease install the missing dependencies and try again."
            
            QMessageBox.critical(None, "Missing Dependencies", error_msg)
            return 1
        
        # Show warnings if any
        if warnings:
            show_startup_info(warnings)
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        logger.info("Application started successfully")
        
        # Run the application event loop
        return app.exec()
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        
        # Try to show error dialog if Qt is available
        try:
            if 'app' in locals():
                QMessageBox.critical(None, "Startup Error", f"Failed to start application:\n\n{e}")
            else:
                print(f"Failed to start application: {e}")
        except:
            print(f"Critical error during startup: {e}")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)