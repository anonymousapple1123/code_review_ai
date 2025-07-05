# llm_interface/qwen_runner.py

import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder"


def stream_code_review(code: str):
    prompt = build_prompt(code)

    payload = {
        "model": MODEL_NAME,
        "stream": True,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer. Provide a detailed review of the following Python code. "
                    "Comment on correctness, bugs, readability, performance, and possible improvements."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[len("data: "):]
                try:
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        yield f"[ERROR] Failed to stream from LLM: {str(e)}"


def stream_follow_up(original_review: str, question: str):
    """
    Sends a follow-up question to the LLM using context from the original review.
    Streams the response token by token.
    """
    payload = {
        "model": MODEL_NAME,
        "stream": True,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI code reviewer continuing a conversation. Use the previous review as context."
            },
            {
                "role": "user",
                "content": f"Here is the review:\n\n{original_review}"
            },
            {
                "role": "user",
                "content": f"Follow-up question:\n\n{question}"
            }
        ]
    }

    try:
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[len("data: "):]
                try:
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        yield f"[ERROR] Failed to stream follow-up: {str(e)}"


def build_prompt(code: str) -> str:
    return f"Please review the following Python code:\n\n```python\n{code}\n```"
