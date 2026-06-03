"""
Configuration module for Supply Chain Optimization Agent.
Handles Anthropic API credentials and model settings.
"""

import os


class Config:
    """Configuration class for Anthropic API and agent settings."""

    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv(
            "ANTHROPIC_MODEL",
            "claude-sonnet-4-5-20250929-v1:0"
        )
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "10"))

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")
        return True


config = Config()
