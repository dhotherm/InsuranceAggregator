"""
Quote agent for retrieving insurance quotes.

In production, this would automate actual quote flows via Playwright.
For the PoC, we use realistic mock calculations based on industry data.
"""

import json
from typing import Dict, Optional
import random


class QuoteAgent:
    """Agent for generating insurance quotes."""

    # Base rates per $1000 coverage (monthly) - approximate industry data
    BASE_RATES = {
        "term_life": {
            "sunlife": 0.08,
            "manulife": 0.075,
            "canadalife": 0.082
        },
        "whole_life": {
            "sunlife": 0.85,
            "manulife": 0.82,
            "canadalife": 0.88
        },
        "critical_illness": {
            "sunlife": 0.45,
            "manulife": 0.42,
            "canadalife": 0.47
        },
        "disability": {
            "sunlife": 2.5,  # per $100 monthly benefit
            "manulife": 2.3,
            "canadalife": 2.6
        }
    }

    def get_quote(
        self,
        carrier: str,
        product_type: str,
        age: int,
        coverage_amount: int = 500000,
        smoker: bool = False,
        term_years: int = 10,
        gender: str = "male"
    ) -> str:
        """
        Get a quote estimate from a carrier.

        Note: These are estimates based on typical industry rates.
        Actual quotes require full underwriting.
        """
        if carrier not in ["sunlife", "manulife", "canadalife"]:
            return json.dumps({"error": f"Unknown carrier: {carrier}"})

        if product_type not in self.BASE_RATES:
            return json.dumps({"error": f"Unknown product type: {product_type}"})

        # Calculate premium
        base_rate = self.BASE_RATES[product_type][carrier]

        if product_type == "disability":
            # Disability is per $100 of monthly benefit
            monthly_benefit = coverage_amount * 0.6 / 12  # 60% of annual income / 12
            units = monthly_benefit / 100
            premium = base_rate * units
        else:
            # Life/CI is per $1000 coverage
            units = coverage_amount / 1000
            premium = base_rate * units

        # Age factor (increases with age)
        age_factor = 1.0
        if age < 30:
            age_factor = 0.7
        elif age < 40:
            age_factor = 1.0
        elif age < 50:
            age_factor = 1.5
        elif age < 60:
            age_factor = 2.5
        else:
            age_factor = 4.0

        premium *= age_factor

        # Smoker factor
        if smoker:
            premium *= 2.5

        # Gender factor (for life insurance)
        if product_type in ["term_life", "whole_life"] and gender == "female":
            premium *= 0.85  # Women typically get lower rates

        # Term factor (for term life)
        if product_type == "term_life":
            term_factor = 1.0 + (term_years - 10) * 0.03
            premium *= term_factor

        # Add some variance for realism
        premium *= random.uniform(0.95, 1.05)
        premium = round(premium, 2)

        # Build response
        quote = {
            "carrier": carrier,
            "carrier_display": self._carrier_display_name(carrier),
            "product_type": product_type,
            "coverage_amount": coverage_amount,
            "term_years": term_years if product_type == "term_life" else None,
            "monthly_premium": premium,
            "annual_premium": round(premium * 12, 2),
            "quote_details": {
                "age": age,
                "smoker": smoker,
                "gender": gender
            },
            "disclaimer": "This is an estimate only. Actual premiums require full medical underwriting and may vary based on health history, occupation, and other factors.",
            "status": "estimate"
        }

        return json.dumps(quote, indent=2)

    def get_multi_carrier_quotes(
        self,
        product_type: str,
        age: int,
        coverage_amount: int = 500000,
        smoker: bool = False,
        term_years: int = 10,
        gender: str = "male"
    ) -> str:
        """Get quotes from all carriers for comparison."""
        quotes = []

        for carrier in ["sunlife", "manulife", "canadalife"]:
            quote_json = self.get_quote(
                carrier=carrier,
                product_type=product_type,
                age=age,
                coverage_amount=coverage_amount,
                smoker=smoker,
                term_years=term_years,
                gender=gender
            )
            quotes.append(json.loads(quote_json))

        # Sort by premium
        quotes.sort(key=lambda x: x.get("monthly_premium", float('inf')))

        return json.dumps({
            "comparison": {
                "product_type": product_type,
                "coverage_amount": coverage_amount,
                "profile": {"age": age, "smoker": smoker, "gender": gender}
            },
            "quotes": quotes,
            "lowest_premium": quotes[0] if quotes else None
        }, indent=2)

    def _carrier_display_name(self, carrier: str) -> str:
        """Get display name for carrier."""
        names = {
            "sunlife": "Sun Life",
            "manulife": "Manulife",
            "canadalife": "Canada Life"
        }
        return names.get(carrier, carrier)
