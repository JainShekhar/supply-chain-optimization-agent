"""
Core agent definition for supply chain optimization.
"""

from strands_mock import Agent
from tools.sandbox_tool import execute_supply_chain_code
from agent.prompts import DYNAMIC_OR_PROMPT
from config import config


def get_agent():
    """Create and return the supply chain agent."""
    return Agent(
        name="SupplyChainOptimizationAgent",
        instructions=DYNAMIC_OR_PROMPT,
        tools=[execute_supply_chain_code],
        model_id=config.bedrock_model_id,
    )


supply_chain_agent = get_agent()
