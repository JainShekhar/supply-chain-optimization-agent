"""
Core agent definition for supply chain optimization.
"""

from anthropic_agent import AnthropicAgent
from tools.sandbox_tool import execute_supply_chain_code
from agent.prompts import DYNAMIC_OR_PROMPT


def get_agent():
    """Create and return the supply chain agent."""
    return AnthropicAgent(
        name="SupplyChainOptimizationAgent",
        instructions=DYNAMIC_OR_PROMPT,
        tools=[execute_supply_chain_code],
        model="claude-sonnet-4-5-20250929-v1:0",
    )


supply_chain_agent = get_agent()
