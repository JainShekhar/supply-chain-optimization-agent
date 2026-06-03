"""
Core agent definition for supply chain optimization.
"""

from strands_agents_sdk import Agent
from tools.sandbox_tool import execute_supply_chain_code
from agent.prompts import DYNAMIC_OR_PROMPT
from config import config


supply_chain_agent = Agent(
    name="SupplyChainOptimizationAgent",
    instructions=DYNAMIC_OR_PROMPT,
    tools=[execute_supply_chain_code],
    model_id=config.bedrock_model_id,
)
