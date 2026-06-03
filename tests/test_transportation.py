"""
Test cases for transportation and linear programming problems.
"""

import pytest
from tools.sandbox_tool import execute_supply_chain_code


class TestTransportationProblem:
    """Test linear programming transportation problems using PuLP."""

    def test_basic_transportation_lp(self):
        """Test Case 3: Transportation Problem (LP with pulp)."""

        code = """
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus

# Problem data
factories = ['A', 'B']
customers = ['1', '2']

supply = {'A': 200, 'B': 300}
demand = {'1': 150, '2': 250}

costs = {
    ('A', '1'): 4,
    ('A', '2'): 6,
    ('B', '1'): 3,
    ('B', '2'): 5,
}

# Create the problem
prob = LpProblem("TransportationProblem", LpMinimize)

# Decision variables: flow from factory to customer
flow = {}
for f in factories:
    for c in customers:
        flow[(f, c)] = LpVariable(f"flow_{f}_to_{c}", lowBound=0)

# Objective: minimize total cost
prob += lpSum([costs[(f, c)] * flow[(f, c)] for f in factories for c in customers]), "TotalCost"

# Supply constraints
for f in factories:
    prob += lpSum([flow[(f, c)] for c in customers]) <= supply[f], f"Supply_{f}"

# Demand constraints
for c in customers:
    prob += lpSum([flow[(f, c)] for f in factories]) >= demand[c], f"Demand_{c}"

# Solve
prob.solve()

# Extract results
status = LpStatus[prob.status]
total_cost = prob.objective.value()

allocation = {}
for f in factories:
    for c in customers:
        allocation[f'{f}_to_{c}'] = flow[(f, c)].varValue

OUTPUT_RESULTS['status'] = status
OUTPUT_RESULTS['total_cost'] = total_cost
OUTPUT_RESULTS['allocation'] = allocation
OUTPUT_RESULTS['A_to_1'] = allocation['A_to_1']
OUTPUT_RESULTS['A_to_2'] = allocation['A_to_2']
OUTPUT_RESULTS['B_to_1'] = allocation['B_to_1']
OUTPUT_RESULTS['B_to_2'] = allocation['B_to_2']
"""

        result = execute_supply_chain_code(code)

        assert result['success'] is True, f"Execution failed: {result.get('error')}"

        results = result['results']
        assert results['status'] == 'Optimal', "Solution should be optimal"
        assert 'total_cost' in results

        total_cost = results['total_cost']
        assert total_cost > 0, "Total cost should be positive"

        assert total_cost <= 2300, "Cost seems too high, check constraints"

        assert 'A_to_1' in results
        assert 'A_to_2' in results
        assert 'B_to_1' in results
        assert 'B_to_2' in results

        total_from_A = results['A_to_1'] + results['A_to_2']
        total_from_B = results['B_to_1'] + results['B_to_2']
        assert total_from_A <= 200, "Factory A supply constraint violated"
        assert total_from_B <= 300, "Factory B supply constraint violated"

        total_to_1 = results['A_to_1'] + results['B_to_1']
        total_to_2 = results['A_to_2'] + results['B_to_2']
        assert abs(total_to_1 - 150) < 0.01, "Customer 1 demand not met"
        assert abs(total_to_2 - 250) < 0.01, "Customer 2 demand not met"

    def test_infeasible_transportation(self):
        """Test that infeasible problems are detected."""

        code = """
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus

# Infeasible: demand exceeds supply
prob = LpProblem("Infeasible", LpMinimize)

x = LpVariable("x", lowBound=0)
y = LpVariable("y", lowBound=0)

prob += x + y, "Cost"
prob += x + y <= 10, "Supply"
prob += x + y >= 20, "Demand"

prob.solve()

OUTPUT_RESULTS['status'] = LpStatus[prob.status]
OUTPUT_RESULTS['is_optimal'] = (LpStatus[prob.status] == 'Optimal')
"""

        result = execute_supply_chain_code(code)
        assert result['success'] is True
        assert result['results']['is_optimal'] is False

    def test_multi_product_allocation(self):
        """Test allocation with multiple products."""

        code = """
from pulp import LpProblem, LpVariable, LpMaximize, LpStatus

# Simple profit maximization with resource constraints
prob = LpProblem("ProductMix", LpMaximize)

# Two products with different profits and resource requirements
product_a = LpVariable("product_a", lowBound=0)
product_b = LpVariable("product_b", lowBound=0)

# Maximize profit: A earns $40, B earns $30
prob += 40 * product_a + 30 * product_b, "TotalProfit"

# Constraints
prob += 2 * product_a + 1 * product_b <= 100, "Labor"
prob += 1 * product_a + 2 * product_b <= 80, "Material"

prob.solve()

OUTPUT_RESULTS['status'] = LpStatus[prob.status]
OUTPUT_RESULTS['product_a_qty'] = product_a.varValue
OUTPUT_RESULTS['product_b_qty'] = product_b.varValue
OUTPUT_RESULTS['max_profit'] = prob.objective.value()
"""

        result = execute_supply_chain_code(code)
        assert result['success'] is True
        assert result['results']['status'] == 'Optimal'
        assert result['results']['max_profit'] > 0


class TestSandboxSecurity:
    """Test sandbox isolation and error handling."""

    def test_syntax_error_handling(self):
        """Verify that syntax errors are caught and reported."""

        code = """
def broken_function(
    print("missing closing parenthesis")
"""

        result = execute_supply_chain_code(code)
        assert result['success'] is False
        assert 'error' in result
        assert 'traceback' in result

    def test_runtime_error_handling(self):
        """Verify that runtime errors are caught."""

        code = """
x = 1 / 0
OUTPUT_RESULTS['should_not_reach'] = True
"""

        result = execute_supply_chain_code(code)
        assert result['success'] is False
        assert 'ZeroDivisionError' in result['error'] or 'division' in result['error']

    def test_missing_output_results(self):
        """Test handling when OUTPUT_RESULTS is not populated."""

        code = """
x = 42
y = x * 2
"""

        result = execute_supply_chain_code(code)
        assert result['success'] is True
        assert result['results'] == {} or result['results'] is None
