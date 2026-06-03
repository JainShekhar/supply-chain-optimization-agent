"""
Agent implementation using Anthropic SDK with tool calling.
"""

import os
from typing import List, Callable, Dict, Any
from anthropic import Anthropic
from anthropic.types import MessageParam, ToolParam


class AnthropicAgent:
    """Agent that uses Claude with tool calling via Anthropic SDK."""

    def __init__(
        self,
        name: str,
        instructions: str,
        tools: List[Callable],
        model: str = "claude-sonnet-4-5-20250929-v1:0",
        max_tokens: int = 4096,
    ):
        self.name = name
        self.instructions = instructions
        self.tool_functions = {tool.__name__: tool for tool in tools}
        self.model = model
        self.max_tokens = max_tokens

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")

        self.client = Anthropic(api_key=api_key)
        self.tool_schemas = self._build_tool_schemas(tools)

    def _build_tool_schemas(self, tools: List[Callable]) -> List[ToolParam]:
        """Build tool schemas from decorated functions."""
        schemas = []
        for tool_func in tools:
            schema: ToolParam = {
                "name": tool_func.__name__,
                "description": tool_func.__doc__ or f"Execute {tool_func.__name__}",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "python_code": {
                            "type": "string",
                            "description": "Python code to execute in the sandbox"
                        }
                    },
                    "required": ["python_code"]
                }
            }
            schemas.append(schema)
        return schemas

    def run(self, user_message: str, max_iterations: int = 10):
        """Run the agent with the given user message."""
        messages: List[MessageParam] = [
            {"role": "user", "content": user_message}
        ]

        for iteration in range(max_iterations):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.instructions,
                messages=messages,
                tools=self.tool_schemas,
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if block.type == "text":
                        yield TextChunk(block.text)
                break

            elif response.stop_reason == "tool_use":
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_use_id = block.id

                        if tool_name in self.tool_functions:
                            try:
                                result = self.tool_functions[tool_name](**tool_input)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": str(result)
                                })
                            except Exception as e:
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": f"Error: {str(e)}",
                                    "is_error": True
                                })
                        else:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": f"Unknown tool: {tool_name}",
                                "is_error": True
                            })

                messages.append({
                    "role": "user",
                    "content": tool_results
                })

            elif response.stop_reason == "max_tokens":
                for block in response.content:
                    if block.type == "text":
                        yield TextChunk(block.text)
                yield TextChunk("\n\n[Response truncated due to length]")
                break

            else:
                for block in response.content:
                    if block.type == "text":
                        yield TextChunk(block.text)
                break

        if messages[-1]["role"] == "assistant":
            for block in messages[-1]["content"]:
                if hasattr(block, 'type') and block.type == "text":
                    yield TextChunk(block.text)


class TextChunk:
    """Represents a chunk of text from the agent response."""

    def __init__(self, text: str):
        self.text = text
        self.content = [self]

    def __str__(self):
        return self.text


def tool(func: Callable) -> Callable:
    """Decorator to mark a function as a tool (no-op, just for documentation)."""
    return func
