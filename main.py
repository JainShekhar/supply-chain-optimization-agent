"""
Main entry point for Supply Chain Optimization Agent.
Simple CLI interface for testing and demonstration.
"""

import sys
from agent import supply_chain_agent
from config import config


def main():
    """Run the supply chain optimization agent CLI."""
    print("=" * 70)
    print("Supply Chain Optimization Agent")
    print("Powered by Anthropic Claude AI")
    print("=" * 70)
    print()

    config.validate()

    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        print("Enter your supply chain optimization problem:")
        print("(or use: python main.py 'your question here')")
        print()
        user_query = input("> ").strip()

    if not user_query:
        print("No query provided. Exiting.")
        return

    print()
    print("Processing your request...")
    print("-" * 70)
    print()

    try:
        response = supply_chain_agent.run(user_query)

        print("Agent Response:")
        print("=" * 70)

        for chunk in response:
            if hasattr(chunk, 'content'):
                for content_block in chunk.content:
                    if hasattr(content_block, 'text'):
                        print(content_block.text, end='', flush=True)
            elif hasattr(chunk, 'text'):
                print(chunk.text, end='', flush=True)

        print()
        print("=" * 70)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
