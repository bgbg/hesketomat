"""LLM service for AI-powered features (OpenAI and DeepSeek)."""
import logging
import os
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLM providers."""

    def __init__(self):
        """Initialize LLM service with API clients."""
        self.openai_client = None
        self.deepseek_client = None

        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OPENAI_API_KEY not found in environment")

        # Initialize DeepSeek client (uses OpenAI SDK with custom base URL)
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_api_key:
            self.deepseek_client = OpenAI(
                api_key=deepseek_api_key,
                base_url="https://api.deepseek.com",
            )
            logger.info("DeepSeek client initialized")
        else:
            logger.warning("DEEPSEEK_API_KEY not found in environment")

    def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        provider: str = "openai",
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """Generate text completion using specified LLM provider."""
        if provider == "openai":
            return self._generate_openai(system_prompt, user_prompt, max_tokens, temperature)
        elif provider == "deepseek":
            return self._generate_deepseek(system_prompt, user_prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate completion using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            raise

    def _generate_deepseek(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate completion using DeepSeek."""
        if not self.deepseek_client:
            raise ValueError("DeepSeek client not initialized. Check DEEPSEEK_API_KEY.")

        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}", exc_info=True)
            raise


# Global LLM service instance
llm_service = LLMService()
