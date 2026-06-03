"""
Test cases for inventory optimization problems.
"""

import pytest
from tools.sandbox_tool import execute_supply_chain_code


class TestEOQOptimization:
    """Test Economic Order Quantity calculations."""

    def test_basic_eoq_calculation(self):
        """Test Case 1: Deterministic Inventory Optimization (EOQ)."""

        code = """
import numpy as np

# Problem parameters
annual_demand = 12000  # units per year
setup_cost = 150  # dollars per order
holding_cost = 3  # dollars per unit per year

# EOQ formula
eoq = np.sqrt((2 * annual_demand * setup_cost) / holding_cost)

# Calculate derived metrics
orders_per_year = annual_demand / eoq
total_annual_cost = (annual_demand / eoq) * setup_cost + (eoq / 2) * holding_cost

# Store results
OUTPUT_RESULTS['eoq'] = round(eoq, 2)
OUTPUT_RESULTS['orders_per_year'] = round(orders_per_year, 2)
OUTPUT_RESULTS['total_annual_cost'] = round(total_annual_cost, 2)
OUTPUT_RESULTS['order_frequency_days'] = round(365 / orders_per_year, 2)
"""

        result = execute_supply_chain_code(code)

        assert result['success'] is True, f"Execution failed: {result.get('error')}"

        results = result['results']
        assert 'eoq' in results, "EOQ not found in results"
        assert 'total_annual_cost' in results, "Total annual cost not found"

        eoq_value = results['eoq']
        assert 1090 <= eoq_value <= 1100, f"EOQ {eoq_value} not close to expected 1095.44"

        assert results['orders_per_year'] > 0
        assert results['total_annual_cost'] > 0

    def test_eoq_edge_case_high_demand(self):
        """Test EOQ with high demand scenario."""

        code = """
import numpy as np

annual_demand = 100000
setup_cost = 500
holding_cost = 10

eoq = np.sqrt((2 * annual_demand * setup_cost) / holding_cost)
OUTPUT_RESULTS['eoq'] = round(eoq, 2)
OUTPUT_RESULTS['valid'] = eoq > 0
"""

        result = execute_supply_chain_code(code)
        assert result['success'] is True
        assert result['results']['valid'] is True


class TestStochasticInventory:
    """Test multi-echelon stochastic inventory optimization."""

    def test_two_stage_serial_system(self):
        """Test Case 2: Multi-Echelon / Stochastic Inventory with stockpyl."""

        code = """
from stockpyl.instances import Item
from stockpyl.supply_chain_network import SupplyChainNetwork
from stockpyl.policy_evaluation import evaluate_policy

# Create downstream retail node (node 0)
retail = Item(
    node_num=0,
    holding_cost=4.0,
    lead_time=1,
    demand_source='normal',
    demand_mean=50,
    demand_sd=10
)

# Create upstream warehouse node (node 1)
warehouse = Item(
    node_num=1,
    holding_cost=1.0,
    lead_time=3,
    demand_source=None
)

# Link: retail gets supply from warehouse
retail.add_successor(warehouse)

# Create network
network = SupplyChainNetwork()
network.add_node(retail)
network.add_node(warehouse)

# Set initial base-stock levels (S policy)
# These are heuristic starting points
retail.inventory_policy.base_stock_level = 75
warehouse.inventory_policy.base_stock_level = 220

# Evaluate the policy
results = evaluate_policy(network, num_periods=500, rand_seed=42)

# Store results
OUTPUT_RESULTS['retail_base_stock'] = retail.inventory_policy.base_stock_level
OUTPUT_RESULTS['warehouse_base_stock'] = warehouse.inventory_policy.base_stock_level
OUTPUT_RESULTS['avg_cost_per_period'] = round(results['cost'], 2)
OUTPUT_RESULTS['retail_node'] = retail.node_num
OUTPUT_RESULTS['warehouse_node'] = warehouse.node_num
"""

        result = execute_supply_chain_code(code)

        assert result['success'] is True, f"Execution failed: {result.get('error')}"

        results = result['results']
        assert 'retail_base_stock' in results
        assert 'warehouse_base_stock' in results

        retail_bs = results['retail_base_stock']
        warehouse_bs = results['warehouse_base_stock']

        assert isinstance(retail_bs, (int, float))
        assert isinstance(warehouse_bs, (int, float))
        assert retail_bs > 0, "Retail base-stock level must be positive"
        assert warehouse_bs > 0, "Warehouse base-stock level must be positive"

        assert 'avg_cost_per_period' in results
        assert results['avg_cost_per_period'] > 0

    def test_stockpyl_network_structure(self):
        """Validate that stockpyl network is correctly structured."""

        code = """
from stockpyl.instances import Item
from stockpyl.supply_chain_network import SupplyChainNetwork

node1 = Item(node_num=0, holding_cost=2.0, lead_time=1)
node2 = Item(node_num=1, holding_cost=1.0, lead_time=2)

node1.add_successor(node2)

network = SupplyChainNetwork()
network.add_node(node1)
network.add_node(node2)

OUTPUT_RESULTS['num_nodes'] = len(network.nodes)
OUTPUT_RESULTS['node1_has_successor'] = len(node1.successors) > 0
"""

        result = execute_supply_chain_code(code)
        assert result['success'] is True
        assert result['results']['num_nodes'] == 2
        assert result['results']['node1_has_successor'] is True
