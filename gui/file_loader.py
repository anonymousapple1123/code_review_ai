# gui/file_loader.py

def load_file_content(file_path: str) -> str:
    """Reads and returns the content of a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {e}")
