"""
Configuration module for Supply Chain Optimization Agent.
Handles AWS Bedrock and model settings.
"""

import os


class Config:
    """Configuration class for AWS Bedrock and agent settings."""

    def __init__(self):
        self.aws_region = os.getenv("AWS_REGION", "us-west-2")
        self.model = os.getenv(
            "ANTHROPIC_MODEL",
            "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        )
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "10"))

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        # AWS credentials are handled automatically by boto3
        # (IAM role, environment variables, or ~/.aws/credentials)
        return True


config = Config()
