"""
Configuration module for Supply Chain Optimization Agent.
Handles AWS Bedrock credentials and model settings.
"""

import os
from typing import Optional


class Config:
    """Configuration class for AWS Bedrock and agent settings."""

    def __init__(self):
        self.aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_session_token = os.getenv("AWS_SESSION_TOKEN")

        self.bedrock_model_id = os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-sonnet-4-6-v1:0"
        )

        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "10"))

    def get_aws_credentials(self) -> dict:
        """Return AWS credentials as a dictionary."""
        credentials = {
            "region_name": self.aws_region
        }

        if self.aws_access_key_id:
            credentials["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            credentials["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            credentials["aws_session_token"] = self.aws_session_token

        return credentials

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.aws_region:
            raise ValueError("AWS_DEFAULT_REGION must be set")
        return True


config = Config()
