# 🧠 Local Code Review GUI App

A modern, privacy-focused Python GUI application for reviewing code using a local Large Language Model (LLM). No internet required, and all data stays on your machine.

---

## ✨ Features

- ✅ **Local LLM-powered reviews** using [Ollama](https://ollama.com/) + [Qwen2.5-Coder](https://huggingface.co/Qwen/Qwen1.5-14B-Chat)
- ✅ **PyQt6 GUI** with native look-and-feel
- ✅ **Secure file picker** for `.py` files
- ✅ **Background threaded execution** (UI never freezes)
- ✅ **Plain-text review output display**
- ✅ **Cross-platform**: Works on Linux, macOS (M-series), and more

---

## 📁 Project Structure

code_review_app/
├── app.py # App entry point
├── gui/
│ ├── main_window.py # Main GUI logic
│ ├── file_loader.py # Load file contents
│ └── review_output.py # (Optional) review rendering
│
├── llm_interface/
│ ├── qwen_runner.py # Sends review requests to Ollama
│ ├── prompt_template.py # Prompt formats (for initial and follow-up)
│ └── review_task.py # Threaded LLM call using QRunnable
│
├── sandbox/
│ ├── docker_manager.py # (Coming soon) sandboxed code execution
│ └── Dockerfile # Secure execution environment
│
├── utils/
│ └── init.py # Future shared tools
│
├── requirements.txt
└── README.md # This file


---

## 🚀 Getting Started

### 1. Clone the Repository

```
git clone https://github.com/yourname/code-review-app.git
cd code-review-app
```

2. Create and Activate Virtual Environment

Using venv:
```
python3 -m venv .venv
source .venv/bin/activate
```

Using conda (optional):

```
conda create -n code_review python=3.11
conda activate code_review
```

3. Install Python Dependencies
```
pip install -r requirements.txt
```
