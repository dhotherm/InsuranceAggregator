"""
Research agent for product information retrieval and comparison.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class InsuranceProduct:
    """Represents an insurance product."""
    carrier: str
    name: str
    product_type: str
    description: str
    min_coverage: int
    max_coverage: int
    features: List[str]
    exclusions: List[str]
    waiting_period: Optional[str]
    renewable: bool
    convertible: bool
    premium_range: Optional[str]
    url: str


class ResearchAgent:
    """Agent for researching and comparing insurance products."""

    def __init__(self, data_dir: str = "./data/products"):
        self.data_dir = Path(data_dir)
        self.products: Dict[str, List[Dict]] = {}
        self._load_products()

    def _load_products(self):
        """Load product data from JSON files."""
        for carrier in ["sunlife", "manulife", "canadalife"]:
            product_file = self.data_dir / f"{carrier}.json"
            if product_file.exists():
                with open(product_file) as f:
                    self.products[carrier] = json.load(f)
            else:
                self.products[carrier] = []

    def search_products(
        self,
        product_type: str,
        carriers: Optional[List[str]] = None,
        min_coverage: Optional[int] = None,
        max_coverage: Optional[int] = None
    ) -> str:
        """
        Search for products matching criteria.

        Returns JSON string for tool response.
        """
        carriers = carriers or ["sunlife", "manulife", "canadalife"]
        results = []

        for carrier in carriers:
            if carrier not in self.products:
                continue

            for product in self.products[carrier]:
                # Filter by product type
                if product.get("product_type") != product_type:
                    continue

                # Filter by coverage range
                if min_coverage and product.get("max_coverage", float('inf')) < min_coverage:
                    continue
                if max_coverage and product.get("min_coverage", 0) > max_coverage:
                    continue

                results.append({
                    "id": f"{carrier}:{product['name']}",
                    "carrier": carrier,
                    "carrier_display": self._carrier_display_name(carrier),
                    **product
                })

        return json.dumps({
            "query": {
                "product_type": product_type,
                "carriers": carriers,
                "min_coverage": min_coverage,
                "max_coverage": max_coverage
            },
            "found": len(results),
            "products": results
        }, indent=2)

    def compare_products(
        self,
        products: List[str],
        criteria: Optional[List[str]] = None
    ) -> str:
        """
        Generate structured comparison of products.

        Args:
            products: List of product IDs (format: "carrier:product_name")
            criteria: Comparison criteria
        """
        default_criteria = [
            "premium_range",
            "coverage_range",
            "features",
            "exclusions",
            "waiting_period",
            "renewable",
            "convertible"
        ]
        criteria = criteria or default_criteria

        comparison = {
            "criteria": criteria,
            "products": []
        }

        for product_id in products:
            try:
                carrier, name = product_id.split(":", 1)
            except ValueError:
                continue

            product_data = self._get_product(carrier, name)
            if product_data:
                comparison["products"].append({
                    "id": product_id,
                    "carrier": carrier,
                    "carrier_display": self._carrier_display_name(carrier),
                    "name": name,
                    "details": {c: product_data.get(c, "N/A") for c in criteria}
                })

        return json.dumps(comparison, indent=2)

    def analyze_coverage_gaps(
        self,
        age: int,
        marital_status: str = "single",
        dependents: int = 0,
        homeowner: bool = False,
        mortgage_amount: int = 0,
        annual_income: int = 0,
        existing_coverage: Optional[List[str]] = None
    ) -> str:
        """
        Analyze insurance coverage gaps based on life situation.
        """
        existing = existing_coverage or []
        recommendations = []

        # Life insurance analysis
        if "life" not in [c.lower() for c in existing]:
            if dependents > 0 or mortgage_amount > 0:
                coverage_needed = max(
                    annual_income * 10,
                    mortgage_amount + (dependents * 100000)
                )
                recommendations.append({
                    "type": "term_life",
                    "priority": "HIGH",
                    "reason": f"With {dependents} dependent(s) and ${mortgage_amount:,} mortgage, life insurance is critical",
                    "suggested_coverage": coverage_needed,
                    "suggested_term": 20 if age < 45 else 10
                })

        # Disability insurance
        if "disability" not in [c.lower() for c in existing]:
            if annual_income > 50000:
                recommendations.append({
                    "type": "disability",
                    "priority": "HIGH",
                    "reason": "Protects your income if you can't work due to illness or injury",
                    "suggested_coverage": int(annual_income * 0.6),
                    "note": "Most policies cover 60-70% of income"
                })

        # Critical illness
        if "critical_illness" not in [c.lower() for c in existing]:
            if age >= 35:
                recommendations.append({
                    "type": "critical_illness",
                    "priority": "MEDIUM",
                    "reason": "Provides lump sum if diagnosed with covered condition",
                    "suggested_coverage": min(annual_income, 100000),
                    "note": "Risk increases significantly after 35"
                })

        # Health/dental (if no employer coverage assumed)
        if "health" not in [c.lower() for c in existing]:
            recommendations.append({
                "type": "health",
                "priority": "MEDIUM",
                "reason": "Covers prescription drugs, dental, vision not covered by provincial health",
                "suggested_coverage": "Extended health + dental plan"
            })

        return json.dumps({
            "profile": {
                "age": age,
                "marital_status": marital_status,
                "dependents": dependents,
                "homeowner": homeowner,
                "mortgage": mortgage_amount,
                "income": annual_income,
                "existing_coverage": existing
            },
            "gaps_identified": len(recommendations),
            "recommendations": recommendations
        }, indent=2)

    def _get_product(self, carrier: str, name: str) -> Optional[Dict]:
        """Get a specific product by carrier and name."""
        if carrier not in self.products:
            return None

        for product in self.products[carrier]:
            if product.get("name") == name:
                return product
        return None

    def _carrier_display_name(self, carrier: str) -> str:
        """Get display name for carrier."""
        names = {
            "sunlife": "Sun Life",
            "manulife": "Manulife",
            "canadalife": "Canada Life"
        }
        return names.get(carrier, carrier)
