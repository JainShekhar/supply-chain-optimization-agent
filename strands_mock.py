"""
Mock implementation of Strands SDK for demo/prototype purposes.
This provides a simplified interface that mimics the Strands agents behavior.
"""

import boto3
import json
from typing import Callable, List, Any, Dict
from functools import wraps


class ToolRegistry:
    """Registry for managing tools available to the agent."""

    def __init__(self):
        self.tools: Dict[str, Dict] = {}

    def register(self, func: Callable, description: str = None) -> Callable:
        """Register a tool function."""
        tool_def = {
            "name": func.__name__,
            "description": description or func.__doc__ or "",
            "function": func,
        }
        self.tools[func.__name__] = tool_def
        return func

    def get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions for the LLM."""
        tools = []
        for tool_name, tool_info in self.tools.items():
            tools.append({
                "toolSpec": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "python_code": {
                                    "type": "string",
                                    "description": "Python code to execute"
                                }
                            },
                            "required": ["python_code"]
                        }
                    }
                }
            })
        return tools

    def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute a registered tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        return self.tools[tool_name]["function"](**tool_input)


_tool_registry = ToolRegistry()


def tool(func: Callable) -> Callable:
    """Decorator to register a function as a tool."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    _tool_registry.register(func, func.__doc__)
    return wrapper


class Agent:
    """Simplified Agent implementation using Amazon Bedrock."""

    def __init__(
        self,
        name: str,
        instructions: str,
        tools: List[Callable],
        model_id: str = "anthropic.claude-sonnet-4-6-v1:0",
    ):
        self.name = name
        self.instructions = instructions
        self.tools = tools
        self.model_id = model_id
        self.bedrock_runtime = None

    def _init_bedrock(self):
        """Initialize Bedrock client lazily."""
        if self.bedrock_runtime is None:
            self.bedrock_runtime = boto3.client("bedrock-runtime")

    def run(self, user_message: str, max_iterations: int = 10):
        """Run the agent with the given user message."""
        self._init_bedrock()

        messages = [{"role": "user", "content": user_message}]

        for iteration in range(max_iterations):
            response = self.bedrock_runtime.converse(
                modelId=self.model_id,
                messages=messages,
                system=[{"text": self.instructions}],
                toolConfig={"tools": _tool_registry.get_tool_definitions()},
            )

            output_message = response["output"]["message"]
            messages.append(output_message)

            stop_reason = response["stopReason"]

            if stop_reason == "end_turn":
                for content_block in output_message.get("content", []):
                    if "text" in content_block:
                        yield TextChunk(content_block["text"])
                break

            elif stop_reason == "tool_use":
                for content_block in output_message.get("content", []):
                    if "toolUse" in content_block:
                        tool_use = content_block["toolUse"]
                        tool_name = tool_use["name"]
                        tool_input = tool_use["input"]
                        tool_use_id = tool_use["toolUseId"]

                        try:
                            tool_result = _tool_registry.execute_tool(tool_name, tool_input)

                            tool_result_content = json.dumps(tool_result)
                        except Exception as e:
                            tool_result_content = json.dumps({"error": str(e)})

                        messages.append({
                            "role": "user",
                            "content": [{
                                "toolResult": {
                                    "toolUseId": tool_use_id,
                                    "content": [{"json": tool_result}]
                                }
                            }]
                        })

            elif stop_reason == "max_tokens":
                yield TextChunk("\n[Response truncated due to length]")
                break

            else:
                break

        for content_block in messages[-1].get("content", []):
            if "text" in content_block:
                yield TextChunk(content_block["text"])


class TextChunk:
    """Represents a chunk of text from the agent response."""

    def __init__(self, text: str):
        self.text = text
        self.content = [self]

    def __str__(self):
        return self.text
