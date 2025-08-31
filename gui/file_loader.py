"""
Enhanced file loading utilities with error handling and validation.

This module provides robust file loading capabilities with proper error
handling, validation, and performance optimizations using C++ backend.
"""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    # Try to import C++ performance module
    import core_performance
    HAS_CPP_BACKEND = True
except ImportError:
    logger.warning("C++ performance module not available. Using Python fallback.")
    HAS_CPP_BACKEND = False


class FileLoadError(Exception):
    """Custom exception for file loading errors."""
    pass


def load_file_content(file_path: str) -> str:
    """
    Load and return the content of a Python file with robust error handling.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        str: The content of the file
        
    Raises:
        FileLoadError: If file cannot be loaded or is invalid
    """
    if not file_path or not isinstance(file_path, str):
        raise FileLoadError("Invalid file path provided")
    
    # Normalize and validate path
    normalized_path = os.path.normpath(file_path)
    
    if not os.path.exists(normalized_path):
        raise FileLoadError(f"File does not exist: {normalized_path}")
    
    if not os.path.isfile(normalized_path):
        raise FileLoadError(f"Path is not a file: {normalized_path}")
    
    # Use C++ backend if available
    if HAS_CPP_BACKEND:
        try:
            if not core_performance.FileProcessor.is_valid_python_file(normalized_path):
                raise FileLoadError(f"File is not a Python file: {normalized_path}")
            return core_performance.FileProcessor.read_file_fast(normalized_path)
        except RuntimeError as e:
            raise FileLoadError(f"C++ backend error: {e}")
    else:
        # Python fallback
        return _load_file_python(normalized_path)


def _load_file_python(file_path: str) -> str:
    """
    Python fallback for file loading.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        str: The content of the file
        
    Raises:
        FileLoadError: If file cannot be loaded
    """
    try:
        # Validate Python file extension
        if not file_path.lower().endswith('.py'):
            raise FileLoadError(f"File is not a Python file: {file_path}")
        
        # Check file size (prevent loading extremely large files)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise FileLoadError(f"File too large: {file_size} bytes. Maximum is 10MB.")
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        logger.info(f"Successfully loaded file: {file_path} ({file_size} bytes)")
        return content
        
    except PermissionError:
        raise FileLoadError(f"Permission denied: {file_path}")
    except UnicodeDecodeError as e:
        raise FileLoadError(f"Unicode decode error: {e}")
    except OSError as e:
        raise FileLoadError(f"OS error reading file: {e}")
    except Exception as e:
        raise FileLoadError(f"Unexpected error loading file: {e}")


def validate_python_file(file_path: str) -> bool:
    """
    Validate if a file is a valid Python file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        bool: True if valid Python file, False otherwise
    """
    try:
        if HAS_CPP_BACKEND:
            return core_performance.FileProcessor.is_valid_python_file(file_path)
        else:
            return (os.path.exists(file_path) and 
                   os.path.isfile(file_path) and 
                   file_path.lower().endswith('.py'))
    except Exception as e:
        logger.error(f"Error validating Python file {file_path}: {e}")
        return False


def get_file_info(file_path: str) -> dict:
    """
    Get detailed information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        dict: File information including size, modification time, etc.
    """
    try:
        stat = os.stat(file_path)
        return {
            'path': os.path.abspath(file_path),
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'is_valid_python': validate_python_file(file_path)
        }
    except OSError as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {}


class FileLoader:
    """
    Enhanced file loader class with caching and validation capabilities.
    """
    
    def __init__(self, max_cache_size: int = 5):
        """Initialize file loader with optional caching."""
        self.max_cache_size = max_cache_size
        self._cache = {}
        self._cache_order = []
    
    def load(self, file_path: str, use_cache: bool = True) -> str:
        """
        Load file content with optional caching.
        
        Args:
            file_path: Path to the file to load
            use_cache: Whether to use caching
            
        Returns:
            str: File content
        """
        normalized_path = os.path.normpath(file_path)
        
        # Check cache first
        if use_cache and normalized_path in self._cache:
            logger.debug(f"Loading from cache: {normalized_path}")
            # Move to end of cache order (LRU)
            self._cache_order.remove(normalized_path)
            self._cache_order.append(normalized_path)
            return self._cache[normalized_path]
        
        # Load from disk
        content = load_file_content(normalized_path)
        
        # Update cache if enabled
        if use_cache:
            self._update_cache(normalized_path, content)
        
        return content
    
    def _update_cache(self, file_path: str, content: str) -> None:
        """Update the internal cache with new content."""
        # Remove oldest item if cache is full
        if len(self._cache) >= self.max_cache_size:
            oldest = self._cache_order.pop(0)
            del self._cache[oldest]
        
        self._cache[file_path] = content
        self._cache_order.append(file_path)
    
    def clear_cache(self) -> None:
        """Clear the file cache."""
        self._cache.clear()
        self._cache_order.clear()
        logger.info("File cache cleared")
    
    def get_cache_info(self) -> dict:
        """Get information about the current cache state."""
        return {
            'cache_size': len(self._cache),
            'max_cache_size': self.max_cache_size,
            'cached_files': list(self._cache_order)
        }
    def get_file_info(self, file_path: str) -> dict:
        try:
            stat = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'is_valid_python': file_path.endswith('.py') and os.path.isfile(file_path)
            }
        except Exception as e:
            return {}