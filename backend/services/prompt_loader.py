"""Utility for loading and managing prompts from YAML configuration."""
import yaml
from pathlib import Path
from typing import Dict, Any


class PromptLoader:
    """Load and manage prompts from YAML configuration."""

    def __init__(self, prompts_file: str = "backend/prompts/prompts.yaml"):
        """Initialize prompt loader."""
        self.prompts_file = Path(prompts_file)
        self._prompts: Dict[str, Any] = {}
        self.load_prompts()

    def load_prompts(self):
        """Load prompts from YAML file."""
        if not self.prompts_file.exists():
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_file}")

        with open(self.prompts_file, "r") as f:
            self._prompts = yaml.safe_load(f)

    def get_search_summary_prompts(self, query: str, search_results: str, background_context: str = None) -> tuple[str, str]:
        """Get system and user prompts for search summarization."""
        config = self._prompts["search_summary"]
        system_prompt = config["system_prompt"].strip()

        # Build context section if provided
        context_section = ""
        if background_context:
            context_section = config["context_prompt_template"].format(
                background_context=background_context
            ).strip()

        user_prompt = config["user_prompt_template"].format(
            query=query,
            context_section=context_section,
            search_results=search_results,
        ).strip()

        return system_prompt, user_prompt

    def get_text_refinement_prompts(self, action: str, text: str) -> tuple[str, str]:
        """Get system and user prompts for text refinement."""
        if action not in ["improve", "shorten", "change_tone"]:
            raise ValueError(f"Invalid refinement action: {action}")

        config = self._prompts["text_refinement"][action]
        system_prompt = config["system_prompt"].strip()
        user_prompt = config["user_prompt_template"].format(text=text).strip()

        return system_prompt, user_prompt

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._prompts.get("configuration", {}).get(key, default)


# Global prompt loader instance
prompt_loader = PromptLoader()
