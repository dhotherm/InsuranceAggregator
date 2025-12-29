"""Tool definitions for the orchestrator."""

TOOLS = [
    {
        "name": "search_products",
        "description": "Search for insurance products across Canadian carriers (Sun Life, Manulife, Canada Life). Use this to find products matching specific criteria like product type, coverage needs, or features.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_type": {
                    "type": "string",
                    "enum": ["term_life", "whole_life", "universal_life", "critical_illness", "disability", "health", "dental", "travel"],
                    "description": "Type of insurance product to search for"
                },
                "carriers": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["sunlife", "manulife", "canadalife"]},
                    "description": "Carriers to search. Defaults to all if not specified."
                },
                "min_coverage": {
                    "type": "integer",
                    "description": "Minimum coverage amount in CAD"
                },
                "max_coverage": {
                    "type": "integer",
                    "description": "Maximum coverage amount in CAD"
                }
            },
            "required": ["product_type"]
        }
    },
    {
        "name": "get_quote",
        "description": "Get an insurance quote from a specific carrier. Returns estimated monthly premium based on provided parameters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "carrier": {
                    "type": "string",
                    "enum": ["sunlife", "manulife", "canadalife"],
                    "description": "Insurance carrier to get quote from"
                },
                "product_type": {
                    "type": "string",
                    "enum": ["term_life", "whole_life", "critical_illness", "disability"],
                    "description": "Type of insurance product"
                },
                "coverage_amount": {
                    "type": "integer",
                    "description": "Coverage amount in CAD",
                    "default": 500000
                },
                "age": {
                    "type": "integer",
                    "description": "Age of the person to be insured"
                },
                "smoker": {
                    "type": "boolean",
                    "description": "Whether the person is a smoker",
                    "default": False
                },
                "term_years": {
                    "type": "integer",
                    "description": "Term length in years (for term life)",
                    "default": 10
                },
                "gender": {
                    "type": "string",
                    "enum": ["male", "female"],
                    "description": "Gender for rate calculation"
                }
            },
            "required": ["carrier", "product_type", "age"]
        }
    },
    {
        "name": "search_documents",
        "description": "Search policy documents, brochures, and FAQs for specific information. Use this to find details about coverage terms, exclusions, conditions, and fine print.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query - what information are you looking for?"
                },
                "carriers": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["sunlife", "manulife", "canadalife"]},
                    "description": "Limit search to specific carriers"
                },
                "document_types": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["policy", "brochure", "faq", "guide", "terms"]},
                    "description": "Types of documents to search"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "compare_products",
        "description": "Generate a structured comparison of specific insurance products across carriers. Use after search_products to do detailed comparison.",
        "input_schema": {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of product IDs to compare (format: carrier:product_name)"
                },
                "criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific criteria to compare (e.g., 'premium', 'coverage', 'exclusions', 'waiting_period')"
                }
            },
            "required": ["products"]
        }
    },
    {
        "name": "analyze_coverage_gaps",
        "description": "Analyze a person's situation and identify potential insurance coverage gaps. Considers life stage, dependents, assets, and existing coverage.",
        "input_schema": {
            "type": "object",
            "properties": {
                "age": {"type": "integer"},
                "marital_status": {
                    "type": "string",
                    "enum": ["single", "married", "common_law", "divorced", "widowed"]
                },
                "dependents": {"type": "integer", "description": "Number of dependents"},
                "homeowner": {"type": "boolean"},
                "mortgage_amount": {"type": "integer", "description": "Outstanding mortgage in CAD"},
                "annual_income": {"type": "integer", "description": "Annual household income in CAD"},
                "existing_coverage": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Types of insurance already held"
                }
            },
            "required": ["age"]
        }
    }
]
