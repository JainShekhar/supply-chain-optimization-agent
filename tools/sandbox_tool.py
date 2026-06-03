"""
Sandbox execution tool for running dynamically generated optimization code.
Provides isolated execution environment with pre-loaded libraries.
"""

import traceback
from typing import Dict, Any
from strands_mock import tool


@tool
def execute_supply_chain_code(python_code: str) -> Dict[str, Any]:
    """
    Execute Python code for supply chain optimization in an isolated sandbox.

    This tool runs dynamically generated Python code with access to optimization
    libraries (pulp, stockpyl, numpy, pandas). The code must write its final
    results to the OUTPUT_RESULTS dictionary.

    Args:
        python_code: Python code string to execute. Must populate OUTPUT_RESULTS dict.

    Returns:
        Dictionary containing:
        - success: Boolean indicating execution success
        - results: Content of OUTPUT_RESULTS if successful
        - error: Error message if execution failed
        - traceback: Full traceback if execution failed
        - code_executed: The code that was executed (for debugging)
    """
    try:
        import pulp
        import stockpyl
        import numpy as np
        import pandas as pd

        execution_globals = {
            "pulp": pulp,
            "LpProblem": pulp.LpProblem,
            "LpVariable": pulp.LpVariable,
            "LpMinimize": pulp.LpMinimize,
            "LpMaximize": pulp.LpMaximize,
            "LpStatus": pulp.LpStatus,
            "lpSum": pulp.lpSum,
            "stockpyl": stockpyl,
            "np": np,
            "pd": pd,
            "OUTPUT_RESULTS": {},
            "__builtins__": __builtins__,
        }

        execution_locals = {}

        exec(python_code, execution_globals, execution_locals)

        output_results = execution_globals.get("OUTPUT_RESULTS", {})

        if not output_results:
            output_results = execution_locals.get("OUTPUT_RESULTS", {})

        return {
            "success": True,
            "results": output_results,
            "code_executed": python_code,
        }

    except Exception as e:
        error_traceback = traceback.format_exc()
        return {
            "success": False,
            "error": str(e),
            "traceback": error_traceback,
            "code_executed": python_code,
        }
