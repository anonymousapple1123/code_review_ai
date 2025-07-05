# llm_interface/qwen_runner.py

import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder"  # make sure this matches what you run in ollama


def run_code_review(code: str) -> str:
    """Sends the Python code to the LLM and returns the review response."""
    prompt = build_prompt(code)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are an expert software engineer tasked with reviewing Python code. Provide feedback on structure, readability, best practices, potential bugs, and suggestions for improvement."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "[No response from LLM]")
    except Exception as e:
        raise RuntimeError(f"Failed to get review from LLM: {e}")


def build_prompt(code: str) -> str:
    """Wraps the code in a prompt that the LLM can understand."""
    return f"Please review the following Python code:\n\n```python\n{code}\n```"
