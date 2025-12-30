#!/usr/bin/env python3
"""
Quick demo bypassing ChromaDB initialization issues
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Disable ChromaDB to avoid HuggingFace downloads
import os
os.environ["CHROMA_DB_IMPL"] = "disabled"

from agents.research_agent import ResearchAgent
from agents.quote_agent import QuoteAgent

def main():
    print("=" * 70)
    print("Insurance Aggregator PoC - Quick Demo")
    print("=" * 70)
    print()

    # Initialize agents
    research = ResearchAgent(data_dir="./data/products")
    quotes = QuoteAgent()

    # Demo 1: Search for term life products
    print("DEMO 1: Search for Term Life Insurance Products")
    print("-" * 70)
    result = research.search_products(product_type="term_life")
    data = json.loads(result)
    print(f"Found {data['found']} products:\n")
    for product in data['products']:
        print(f"  • {product['carrier_display']}: {product['name']}")
        print(f"    Coverage: ${product['min_coverage']:,} - ${product['max_coverage']:,}")
        print(f"    Premium: {product['premium_range']}")
        print()

    # Demo 2: Get quotes from all carriers
    print("\n" + "=" * 70)
    print("DEMO 2: Get Term Life Quotes - $500K Coverage, Age 35, Non-Smoker")
    print("-" * 70)
    print()

    for carrier in ["sunlife", "manulife", "canadalife"]:
        quote_json = quotes.get_quote(
            carrier=carrier,
            product_type="term_life",
            age=35,
            coverage_amount=500000,
            smoker=False,
            gender="male",
            term_years=10
        )
        quote = json.loads(quote_json)
        print(f"{quote['carrier_display']}:")
        print(f"  Monthly Premium: ${quote['monthly_premium']:.2f}")
        print(f"  Annual Premium: ${quote['annual_premium']:.2f}")
        print()

    # Demo 3: Coverage gap analysis
    print("\n" + "=" * 70)
    print("DEMO 3: Coverage Gap Analysis")
    print("Profile: 38 years old, married, 2 kids, $500K mortgage, $150K income")
    print("-" * 70)
    print()

    result = research.analyze_coverage_gaps(
        age=38,
        marital_status="married",
        dependents=2,
        homeowner=True,
        mortgage_amount=500000,
        annual_income=150000,
        existing_coverage=[]
    )
    data = json.loads(result)
    print(f"Coverage Gaps Identified: {data['gaps_identified']}\n")
    for rec in data['recommendations']:
        print(f"  {rec['priority']} PRIORITY: {rec['type'].replace('_', ' ').title()}")
        print(f"  Reason: {rec['reason']}")
        if 'suggested_coverage' in rec:
            print(f"  Suggested Coverage: ${rec['suggested_coverage']:,}")
        print()

    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
