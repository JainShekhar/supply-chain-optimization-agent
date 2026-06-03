# Supply Chain Optimization Agent

A prototype/demo application using the AWS Strands Agents SDK to solve supply chain optimization problems through natural language interaction. The agent dynamically generates and executes Python code using open-source Operations Research libraries.

## Overview

This agent accepts natural language descriptions of supply chain problems and automatically:
1. Analyzes the problem type
2. Selects the appropriate optimization library
3. Generates Python code to solve the problem
4. Executes the code in a secure sandbox
5. Returns results in natural language

## Supported Problem Types

### Linear & Integer Programming (PuLP)
- Transportation and allocation problems
- Production planning
- Resource optimization
- Network flow problems
- Cost minimization/profit maximization

### Inventory Optimization
- Economic Order Quantity (EOQ)
- Multi-echelon inventory systems (Stockpyl)
- Base-stock policies
- Stochastic demand modeling
- Safety stock calculations

## Architecture

```
┌─────────────────┐
│  User Question  │
│  (Natural Lang) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   Strands Agent (LLM)   │
│  - Analyzes problem     │
│  - Generates code       │
│  - Self-corrects errors │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Sandbox Execution Tool │
│  - Isolated environment │
│  - Pre-loaded libraries │
│  - Error capture        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Optimization Libraries │
│  - PuLP (LP/MIP)        │
│  - Stockpyl (Inventory) │
│  - NumPy, Pandas        │
└─────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.11+
- AWS credentials configured for Amazon Bedrock access
- Git

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd supply-chain-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure AWS credentials:
```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

## Usage

### Command Line Interface

```bash
python main.py "Your supply chain question here"
```

Or interactive mode:
```bash
python main.py
```

### Example Queries

**Economic Order Quantity:**
```bash
python main.py "We have annual demand of 12,000 units, setup cost of $150 per order, and holding cost of $3 per unit per year. What is our optimal order quantity?"
```

**Transportation Problem:**
```bash
python main.py "Minimize transportation costs. Factory A has 200 units, Factory B has 300 units. Customer 1 needs 150 units, Customer 2 needs 250 units. Costs: A→1=$4, A→2=$6, B→1=$3, B→2=$5. What's the optimal allocation?"
```

**Multi-Echelon Inventory:**
```bash
python main.py "Optimize a two-stage serial inventory system. Retail node: holding cost $4, lead time 1 day. Warehouse: holding cost $1, lead time 3 days. Demand is normal with mean 50, std dev 10. Find optimal base-stock levels."
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific test files:
```bash
pytest tests/test_inventory.py -v
pytest tests/test_transportation.py -v
```

### Test Coverage

- **EOQ Optimization**: Validates deterministic inventory calculations
- **Multi-Echelon Systems**: Tests stochastic inventory with Stockpyl
- **Transportation LP**: Verifies linear programming solutions
- **Error Handling**: Confirms sandbox security and error recovery

## Project Structure

```
supply-chain-agent/
├── agent/
│   ├── __init__.py
│   ├── core_agent.py      # Agent definition
│   └── prompts.py          # System prompts with library syntax
├── tools/
│   ├── __init__.py
│   └── sandbox_tool.py     # Secure code execution environment
├── tests/
│   ├── __init__.py
│   ├── test_inventory.py   # Inventory optimization tests
│   └── test_transportation.py  # LP/transportation tests
├── config.py               # AWS and model configuration
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
└── README.md
```

## Configuration

### Environment Variables

- `AWS_DEFAULT_REGION`: AWS region for Bedrock (default: us-east-1)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `BEDROCK_MODEL_ID`: Model to use (default: anthropic.claude-sonnet-4-6-v1:0)
- `MAX_ITERATIONS`: Max agent iterations (default: 10)

### Optimization Libraries

**PuLP**
- Uses the bundled CBC solver (free, open-source)
- Supports LP and MILP problems
- No additional solver installation required

**Stockpyl**
- Multi-echelon inventory optimization
- Stochastic demand modeling
- Base-stock and (s,S) policies

## Technical Details

### Code Interpreter Pattern

The agent uses a "code interpreter" approach where:
1. The LLM generates executable Python code
2. Code runs in an isolated sandbox with pre-imported libraries
3. Results are captured in a dedicated `OUTPUT_RESULTS` dictionary
4. Errors trigger automatic retry with corrected code

### Security

- Code executes in a restricted `exec()` environment
- Only pre-approved libraries are accessible
- No file system or network access
- All execution is sandboxed and isolated

## Limitations

- Requires AWS Bedrock access (Claude models)
- PuLP uses CBC solver (may not scale to very large problems)
- Stockpyl policy optimization uses simulation, not analytical methods
- No persistent state between queries

## Future Enhancements

- Support for additional solvers (Gurobi, CPLEX)
- Visualization of optimization results
- Multi-turn conversations with context
- Batch processing of multiple scenarios
- Export to various formats (Excel, JSON, PDF reports)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions:
- Open a GitHub issue
- Check the test suite for examples
- Review the prompts in `agent/prompts.py` for syntax reference

## Acknowledgments

Built with:
- [AWS Strands Agents SDK](https://github.com/awslabs/strands)
- [PuLP](https://github.com/coin-or/pulp)
- [Stockpyl](https://github.com/LarrySnyder/stockpyl)
- Amazon Bedrock (Claude models)
