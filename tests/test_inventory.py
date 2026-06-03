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
        assert bool(result['results']['valid']) is True


class TestStochasticInventory:
    """Test multi-echelon stochastic inventory optimization."""

    def test_two_stage_serial_system(self):
        """Test Case 2: Multi-Echelon / Stochastic Inventory with newsvendor approach."""

        code = """
import numpy as np
from scipy import stats

# Two-stage serial inventory chain parameters
# Downstream retail node
retail_holding_cost = 4.0
retail_lead_time = 1  # days
demand_mean = 50
demand_std = 10

# Upstream warehouse hub
warehouse_holding_cost = 1.0
warehouse_lead_time = 3  # days

# Calculate safety stock using newsvendor approach
# For retail: consider lead time demand variability
retail_lead_time_demand_std = demand_std * np.sqrt(retail_lead_time)
retail_cycle_service_level = 0.95  # 95% service level
retail_z_score = stats.norm.ppf(retail_cycle_service_level)
retail_safety_stock = retail_z_score * retail_lead_time_demand_std
retail_base_stock = demand_mean * retail_lead_time + retail_safety_stock

# For warehouse: cumulative lead time from warehouse perspective
total_lead_time = retail_lead_time + warehouse_lead_time
warehouse_lead_time_demand_std = demand_std * np.sqrt(total_lead_time)
warehouse_z_score = stats.norm.ppf(retail_cycle_service_level)
warehouse_safety_stock = warehouse_z_score * warehouse_lead_time_demand_std
warehouse_base_stock = demand_mean * total_lead_time + warehouse_safety_stock

# Estimate average holding cost per period
avg_cost_per_period = (
    retail_holding_cost * (retail_base_stock / 2) +
    warehouse_holding_cost * (warehouse_base_stock / 2)
)

OUTPUT_RESULTS['retail_base_stock'] = int(np.ceil(retail_base_stock))
OUTPUT_RESULTS['warehouse_base_stock'] = int(np.ceil(warehouse_base_stock))
OUTPUT_RESULTS['avg_cost_per_period'] = round(avg_cost_per_period, 2)
OUTPUT_RESULTS['retail_safety_stock'] = int(np.ceil(retail_safety_stock))
OUTPUT_RESULTS['warehouse_safety_stock'] = int(np.ceil(warehouse_safety_stock))
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
        """Validate multi-stage inventory calculation using basic formulas."""

        code = """
import numpy as np

# Simple two-stage inventory calculation
# Stage 1: Retail (downstream)
stage1_holding_cost = 2.0
stage1_lead_time = 1
stage1_demand_per_period = 100

# Stage 2: Warehouse (upstream)
stage2_holding_cost = 1.0
stage2_lead_time = 2
stage2_demand_per_period = 100  # same as retail

# Calculate average inventory levels (simplified)
stage1_avg_inventory = stage1_demand_per_period * stage1_lead_time
stage2_avg_inventory = stage2_demand_per_period * stage2_lead_time

# Calculate costs
stage1_cost = stage1_holding_cost * stage1_avg_inventory
stage2_cost = stage2_holding_cost * stage2_avg_inventory
total_system_cost = stage1_cost + stage2_cost

OUTPUT_RESULTS['num_stages'] = 2
OUTPUT_RESULTS['stage1_inventory'] = stage1_avg_inventory
OUTPUT_RESULTS['stage2_inventory'] = stage2_avg_inventory
OUTPUT_RESULTS['total_cost'] = total_system_cost
OUTPUT_RESULTS['has_multi_stage'] = True
"""

        result = execute_supply_chain_code(code)
        assert result['success'] is True
        assert result['results']['num_stages'] == 2
        assert bool(result['results']['has_multi_stage']) is True
