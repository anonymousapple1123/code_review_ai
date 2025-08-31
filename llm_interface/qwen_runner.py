"""
Enhanced LLM interface with improved error handling and streaming capabilities.

This module provides a robust interface for communicating with the Ollama API
with proper error handling, retry logic, and performance optimizations.
"""

import requests
import json
import time
import logging
from typing import Iterator, Optional, Dict, Any
from contextlib import contextmanager

from config.app_config import config

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMConnectionError(LLMError):
    """Exception for connection-related LLM errors."""
    pass


class LLMResponseError(LLMError):
    """Exception for LLM response parsing errors."""
    pass


class LLMTimeoutError(LLMError):
    """Exception for LLM timeout errors."""
    pass


class EnhancedLLMClient:
    """
    Enhanced LLM client with robust error handling and retry logic.
    """
    
    def __init__(self):
        """Initialize the LLM client with configuration."""
        self.api_url = config.ollama_api_url
        self.model_name = config.model_name
        self.timeout = config.request_timeout
        self.max_retries = config.max_retries
        
        # Create a reusable session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CodeReviewApp/1.0'
        })
        
        logger.info(f"Initialized LLM client for model: {self.model_name}")
    
    def __del__(self):
        """Cleanup session on destruction."""
        if hasattr(self, 'session'):
            self.session.close()
    
    @contextmanager
    def _handle_request_errors(self):
        """Context manager for handling common request errors."""
        try:
            yield
        except requests.exceptions.ConnectionError as e:
            raise LLMConnectionError(f"Failed to connect to LLM service: {e}")
        except requests.exceptions.Timeout as e:
            raise LLMTimeoutError(f"LLM request timed out: {e}")
        except requests.exceptions.HTTPError as e:
            raise LLMResponseError(f"HTTP error from LLM service: {e}")
        except requests.exceptions.RequestException as e:
            raise LLMError(f"Request error: {e}")
    
    def _create_review_payload(self, code: str) -> Dict[str, Any]:
        """Create the payload for code review requests."""
        system_message = (
            "You are an expert software engineer and code reviewer. "
            "Provide a comprehensive, constructive review of the provided Python code. "
            "Focus on:\n"
            "1. Code correctness and potential bugs\n"
            "2. Code style and readability\n"
            "3. Performance considerations\n"
            "4. Security concerns\n"
            "5. Best practices and improvements\n"
            "6. Documentation and comments\n\n"
            "Format your response in clear, structured markdown."
        )
        
        user_message = f"Please review the following Python code:\n\n```python\n{code}\n```"
        
        return {
            "model": self.model_name,
            "stream": True,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        }
    
    def _create_followup_payload(self, original_review: str, question: str) -> Dict[str, Any]:
        """Create the payload for follow-up questions."""
        system_message = (
            "You are continuing a code review conversation. "
            "Use the previous review as context and answer the user's follow-up question "
            "in a helpful and detailed manner."
        )
        
        return {
            "model": self.model_name,
            "stream": True,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Previous review:\n\n{original_review}"},
                {"role": "user", "content": f"Follow-up question: {question}"}
            ]
        }
    
    def _stream_response(self, payload: Dict[str, Any]) -> Iterator[str]:
        """
        Stream response from the LLM API with retry logic.
        
        Args:
            payload: Request payload
            
        Yields:
            str: Individual tokens from the response
        """
        for attempt in range(self.max_retries + 1):
            try:
                with self._handle_request_errors():
                    response = self.session.post(
                        self.api_url,
                        json=payload,
                        stream=True,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    
                    yield from self._process_stream(response)
                    return  # Success, exit retry loop
                    
            except (LLMConnectionError, LLMTimeoutError) as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts failed: {e}")
                    raise
            except (LLMResponseError, LLMError) as e:
                logger.error(f"Non-retryable error: {e}")
                raise
    
    def _process_stream(self, response: requests.Response) -> Iterator[str]:
        """
        Process streaming response and extract tokens.
        
        Args:
            response: Streaming HTTP response
            
        Yields:
            str: Individual tokens
        """
        try:
            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode("utf-8")  # decode bytes to str
                if line.startswith("data: "):
                    line = line[6:]  # Remove 'data: ' prefix
                
                try:
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token
                        
                    # Check for completion
                    if data.get("done", False):
                        logger.debug("Stream completed successfully")
                        break
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON line: {line}. Error: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing stream: {e}")
            raise LLMResponseError(f"Stream processing error: {e}")
    
    def stream_code_review(self, code: str) -> Iterator[str]:
        """
        Stream a code review response.
        
        Args:
            code: Python code to review
            
        Yields:
            str: Tokens from the review response
        """
        if not code or not code.strip():
            raise LLMError("Empty code provided for review")
        
        # Truncate very large code samples
        max_code_length = config.max_conversation_length // 2
        if len(code) > max_code_length:
            code = code[:max_code_length] + "\n\n# ... (truncated for length) ..."
            logger.warning(f"Code truncated to {max_code_length} characters")
        
        payload = self._create_review_payload(code)
        logger.info(f"Starting code review stream for {len(code)} characters of code")
        
        yield from self._stream_response(payload)
    
    def stream_follow_up(self, original_review: str, question: str) -> Iterator[str]:
        """
        Stream a follow-up response.
        
        Args:
            original_review: The original review text
            question: Follow-up question
            
        Yields:
            str: Tokens from the follow-up response
        """
        if not question or not question.strip():
            raise LLMError("Empty question provided for follow-up")
        
        # Truncate conversation if too long
        max_review_length = config.max_conversation_length // 2
        if len(original_review) > max_review_length:
            # Keep the end of the review (more recent context)
            original_review = "...\n\n" + original_review[-max_review_length:]
            logger.warning(f"Review truncated to {max_review_length} characters")
        
        payload = self._create_followup_payload(original_review, question)
        logger.info(f"Starting follow-up stream for question: {question[:50]}...")
        
        yield from self._stream_response(payload)
    
    def test_connection(self) -> bool:
        """
        Test connection to the LLM service.
        
        Returns:
            bool: True if connection successful
        """
        try:
            response = self.session.get(
                self.api_url.replace('/api/chat', '/api/tags'),
                timeout=5.0
            )
            response.raise_for_status()
            logger.info("LLM connection test successful")
            return True
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False


# Global client instance
llm_client = EnhancedLLMClient()


# Backward compatibility functions
def stream_code_review(code: str) -> Iterator[str]:
    """Backward compatibility function for code review streaming."""
    return llm_client.stream_code_review(code)


def stream_follow_up(original_review: str, question: str) -> Iterator[str]:
    """Backward compatibility function for follow-up streaming."""
    return llm_client.stream_follow_up(original_review, question)