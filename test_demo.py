#!/usr/bin/env python3
"""
Test the Insurance Aggregator PoC
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agents import InsuranceOrchestrator

def main():
    print("=" * 60)
    print("Insurance Aggregator PoC - Demo Test")
    print("=" * 60)
    print()

    orchestrator = InsuranceOrchestrator(data_dir="./data")

    # Test query
    query = "Get me term life insurance quotes from all three carriers for $500,000 coverage. I'm 35, non-smoker, male."

    print(f"Query: {query}")
    print()
    print("Processing...")
    print()

    response = orchestrator.process(query)

    print("=" * 60)
    print("RESPONSE:")
    print("=" * 60)
    print()
    print(response)
    print()

if __name__ == "__main__":
    main()
