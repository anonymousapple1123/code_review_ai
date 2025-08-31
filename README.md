# 🧠 Code Review Assistant - Enhanced Edition

A modern, high-performance Python GUI application for reviewing code using a local Large Language Model (LLM). Features hybrid Python-C++ architecture for optimal performance, complete privacy, and professional code analysis.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### Core Functionality
- 🤖 **Local LLM-powered reviews** using [Ollama](https://ollama.com/) + [Qwen2.5-Coder](https://huggingface.co/Qwen/Qwen2.5-Coder)
- 🖥️ **Modern PyQt6 GUI** with native look-and-feel
- 📁 **Smart file picker** with validation for Python files
- 🔒 **Complete privacy** - all processing stays on your machine
- 💬 **Interactive follow-up questions** for deeper analysis

### Performance Enhancements
- ⚡ **Hybrid C++ backend** for performance-critical operations
- 🚄 **Adaptive streaming** with intelligent buffering
- 🧵 **Multi-threaded execution** (UI never freezes)
- 📊 **Real-time progress tracking** and status updates
- 💾 **Efficient memory management** with conversation limits

### Professional Features
- 🎨 **Dark/Light theme support** with system integration
- 📝 **Enhanced markdown rendering** with syntax highlighting
- 🔧 **Comprehensive error handling** and retry logic
- 📋 **Connection testing** and health monitoring
- 🗂️ **File caching** for improved performance
- ⚙️ **Configurable settings** via environment variables and config files

---

## 🏗️ Architecture

The application uses a **hybrid Python-C++ architecture** for optimal performance:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python GUI    │◄──►│   Python Bridge  │◄──►│   C++ Core      │
│   (PyQt6)       │    │   (pybind11)     │    │   (Performance) │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • UI Components │    │ • Task Management│    │ • Text Streaming│
│ • Event Handling│    │ • Error Handling │    │ • Buffer Mgmt   │
│ • Theme System  │    │ • Config System  │    │ • File I/O      │
│ • User Input    │    │ • Async Bridge   │    │ • Threading     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 📁 Project Structure

```
code_review_app/
├── 📱 app.py                    # Main application entry point
├── 🔧 build.py                 # Build script for C++ components
├── 📋 requirements.txt         # Python dependencies
├── ⚙️ setup.py                 # C++ module build configuration
├── 🏗️ CMakeLists.txt          # CMake build configuration
│
├── 📱 gui/                     # GUI components
│   ├── main_window.py          # Enhanced main window with optimizations
│   └── file_loader.py          # Robust file loading with C++ backend
│
├── 🤖 llm_interface/           # LLM communication layer
│   ├── qwen_runner.py          # Enhanced LLM client with retry logic
│   └── review_task.py          # Optimized task management with C++ streaming
│
├── ⚡ core_cpp/               # C++ performance modules
│   └── text_streamer.cpp       # High-performance text streaming and buffering
│
├── ⚙️ config/                  # Configuration management
│   └── app_config.py           # Centralized configuration system
│
├── 🧪 sandbox/                # Future: sandboxed code execution
├── 📊 utils/                   # Utility modules
└── 🧪 test_files/             # Test files and examples
```

---

## 🚀 Quick Start

### 1. Prerequisites

**System Requirements:**
- Python 3.8 or higher
- CMake 3.12 or higher
- C++ compiler (GCC/Clang/MSVC)
- Ollama with Qwen2.5-Coder model

**Install Ollama & Model:**
```bash
# Install Ollama (visit https://ollama.com for platform-specific instructions)

# Pull the code review model
ollama pull qwen2.5-coder

# Start the model (keep running in background)
ollama run qwen2.5-coder
```

### 2. Quick Installation

**Option A: Automated Build (Recommended)**
```bash
# Clone the repository
git clone https://github.com/yourusername/code-review-app.git
cd code-review-app

# Run the automated build script
python build.py
```

**Option B: Manual Installation**
```bash
# Clone and enter directory
git clone https://github.com/yourusername/code-review-app.git
cd code-review-app

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Build C++ performance module
python setup.py build_ext --inplace

# Run the application
python app.py
```

### 3. First Run

1. **Launch the application:**
   ```bash
   python app.py
   # OR use the generated run scripts:
   ./run.sh        # Unix/Linux/macOS
   # run.bat       # Windows
   ```

2. **Test LLM connection:** Click the "🔗 Test LLM" button to verify Ollama is running

3. **Select a Python file:** Click "📂 Select File" and choose a `.py` file

4. **Get code review:** Click "🔍 Review Code" and watch the analysis stream in real-time

5. **Ask follow-up questions:** Use the input box to ask specific questions about the code

---

## ⚙️ Configuration

The application supports flexible configuration through multiple methods:

### Environment Variables
```bash
export OLLAMA_API_URL="http://localhost:11434/api/chat"
export MODEL_NAME="qwen2.5-coder"
export BUFFER_SIZE=20
export FLUSH_INTERVAL_MS=100
export UI_THEME="dark"
export LOG_LEVEL="INFO"
```

### Configuration File
The app creates `~/.code_review_app/config.json`:
```json
{
  "ollama_api_url": "http://localhost:11434/api/chat",
  "model_name": "qwen2.5-coder",
  "buffer_size": 20,
  "flush_interval_ms": 100,
  "max_conversation_length": 50000,
  "ui_theme": "dark",
  "window_width": 1200,
  "window_height": 800
}
```

---

## 🎯 Usage Examples

### Basic Code Review
1. Select a Python file with the file picker
2. Click "Review Code" to get comprehensive analysis
3. View real-time streaming results with syntax highlighting

### Interactive Follow-up
```
User: "How can I improve the performance of this function?"
Assistant: [Detailed performance analysis with specific suggestions]

User: "Show me an example of the optimization you mentioned"
Assistant: [Code example with explanations]
```

### Advanced Features
- **Theme Toggle:** Switch between light and dark modes
- **Progress Tracking:** Real-time status updates during processing
- **Error Recovery:** Automatic retry with exponential backoff
- **Connection Testing:** Verify LLM service availability

---

## 🔧 Development

### Building from Source

**Install Development Dependencies:**
```bash
pip install -r requirements.txt
pip install pytest pytest-qt black flake8  # Additional dev tools
```

**Build C++ Components:**
```bash
# Using CMake (preferred)
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .

# OR using setup.py
python setup.py build_ext --inplace
```

**Run Tests:**
```bash
pytest tests/                    # Unit tests
python -m pytest --qt-gui       # GUI tests
```

**Code Formatting:**
```bash
black .                          # Format Python code
flake8 .                         # Check code style
```

### Performance Profiling

The application includes built-in performance monitoring:

```python
# Enable performance logging
export LOG_LEVEL=DEBUG

# Monitor with built-in tools
import psutil
import memory_profiler
```

---

## 🐛 Troubleshooting

### Common Issues

**"C++ performance module not available"**
- Run `python build.py` to build the C++ components
- Ensure CMake and a C++ compiler are installed
- The app will work with Python fallback (reduced performance)

**"Failed to connect to LLM service"**
- Verify Ollama is installed and running: `ollama --version`
- Check the model is available: `ollama list`
- Start the model: `ollama run qwen2.5-coder`
- Test connection manually: `curl http://localhost:11434/api/tags`

**"GUI freezing or slow performance"**
- Build the C++ performance module for optimal streaming
- Reduce buffer size in configuration
- Check system memory usage

**"File loading errors"**
- Ensure the selected file is a valid Python file (.py extension)
- Check file permissions and encoding
- File size limit is 10MB

### Performance Optimization

**For Best Performance:**
1. Build C++ performance modules
2. Use SSD storage for faster file I/O
3. Ensure adequate RAM (8GB+ recommended)
4. Close unnecessary applications to free CPU resources

**Memory Usage:**
- The app limits conversation history to prevent memory bloat
- Large code files are automatically truncated
- File caching is limited to 5 recent files

---

## 🛣️ Roadmap

### Version 2.1 (Next Release)
- [ ] **Multi-file project analysis** - Analyze entire codebases
- [ ] **Additional language support** - C++, Java, JavaScript
- [ ] **Code execution sandbox** - Safe code testing environment
- [ ] **Export functionality** - Save reviews as PDF/HTML

### Version 2.2 (Future)
- [ ] **Plugin system** - Extensible architecture for custom analyzers
- [ ] **Cloud LLM support** - Optional integration with remote models
- [ ] **Team collaboration** - Share and discuss reviews
- [ ] **CI/CD integration** - Automated code review in pipelines

### Performance & Quality
- [ ] **Advanced caching** - Intelligent review caching
- [ ] **Real-time collaboration** - Live editing and review
- [ ] **Custom model training** - Fine-tune models for specific codebases

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** and create a feature branch
2. **Install development dependencies:** `pip install -r requirements.txt`
3. **Make your changes** following the existing code style
4. **Run tests:** `pytest tests/`
5. **Submit a pull request** with a clear description

### Development Guidelines
- Follow PEP 8 for Python code
- Use modern C++17 features for C++ components
- Include tests for new functionality
- Update documentation for user-facing changes

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**TL;DR:** Use it, modify it, distribute it, make it better. Just don't blame us if something goes wrong! 😄

---

## 🙏 Acknowledgments

- **[Ollama](https://ollama.com/)** - For making local LLM deployment simple
- **[Qwen Team](https://github.com/QwenLM/Qwen)** - For the excellent code-focused language model
- **[PyQt](https://www.riverbankcomputing.com/software/pyqt/)** - For the powerful GUI framework
- **[pybind11](https://github.com/pybind/pybind11)** - For seamless Python-C++ integration

---

## 📬 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/yourusername/code-review-app/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/code-review-app/discussions)
- **Email:** [your.email@example.com](mailto:your.email@example.com)

---

**⭐ If you find this project helpful, please consider giving it a star on GitHub!**