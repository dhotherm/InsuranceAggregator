"""
Main orchestration agent using Claude as the reasoning engine.
Routes queries to specialized agents and composes responses.
"""

import os
import json
from typing import Dict, List, Any, Optional
import anthropic
from dotenv import load_dotenv

from .tools import TOOLS
from .research_agent import ResearchAgent
from .quote_agent import QuoteAgent
from .document_agent import DocumentAgent

load_dotenv()


class InsuranceOrchestrator:
    """Orchestrates insurance queries across multiple specialized agents."""

    SYSTEM_PROMPT = """You are an AI insurance advisor helping Canadians understand and compare insurance options across Sun Life, Manulife, and Canada Life.

Your role is to:
1. Understand the user's insurance needs based on their life situation
2. Research relevant products across all three major carriers
3. Provide clear, unbiased comparisons highlighting pros and cons
4. Identify coverage gaps and make recommendations
5. Explain policy details in plain language

You have access to these tools:
- search_products: Find insurance products matching criteria
- get_quote: Get premium estimates from specific carriers
- search_documents: Search policy documents for specific information
- compare_products: Generate side-by-side comparisons
- analyze_coverage_gaps: Identify insurance gaps based on life situation

Guidelines:
- Always search across ALL carriers unless the user specifies one
- Be transparent about limitations (estimates, not guaranteed quotes)
- Highlight important exclusions and waiting periods
- Use simple language, avoid jargon
- When comparing, use tables for clarity
- Proactively mention things the user might not think to ask about

Remember: You're demonstrating how an AI aggregator could own the customer relationship. Make the experience so good that users would never need to visit individual carrier websites."""

    def __init__(self, data_dir: str = "./data"):
        self.client = anthropic.Anthropic()
        self.data_dir = data_dir

        # Initialize specialized agents
        self.research = ResearchAgent(data_dir=f"{data_dir}/products")
        self.quotes = QuoteAgent()
        self.documents = DocumentAgent(
            docs_dir=f"{data_dir}/documents",
            vectors_dir=f"{data_dir}/vectors"
        )

        self.conversation_history: List[Dict] = []

    def process(self, user_message: str, reset_history: bool = False) -> str:
        """
        Process a user message through the orchestration loop.

        Args:
            user_message: The user's query
            reset_history: Whether to clear conversation history

        Returns:
            The assistant's response
        """
        if reset_history:
            self.conversation_history = []

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Call Claude with tools
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=self.SYSTEM_PROMPT,
            tools=TOOLS,
            messages=self.conversation_history
        )

        # Handle tool use loop
        while response.stop_reason == "tool_use":
            # Execute all tool calls
            tool_results = self._execute_tools(response.content)

            # Add assistant response and tool results to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })

            # Continue the conversation
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.conversation_history
            )

        # Extract final text response
        final_response = self._extract_text(response.content)

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response.content
        })

        return final_response

    def _execute_tools(self, content: List) -> List[Dict]:
        """Execute tool calls and return results."""
        results = []

        for block in content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                # Route to appropriate agent
                try:
                    result = self._call_tool(tool_name, tool_input)
                except Exception as e:
                    result = json.dumps({"error": str(e)})

                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        return results

    def _call_tool(self, name: str, inputs: Dict) -> str:
        """Route tool call to appropriate agent."""
        if name == "search_products":
            return self.research.search_products(**inputs)
        elif name == "get_quote":
            return self.quotes.get_quote(**inputs)
        elif name == "search_documents":
            return self.documents.search(**inputs)
        elif name == "compare_products":
            return self.research.compare_products(**inputs)
        elif name == "analyze_coverage_gaps":
            return self.research.analyze_coverage_gaps(**inputs)
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    def _extract_text(self, content: List) -> str:
        """Extract text from response content blocks."""
        text_parts = []
        for block in content:
            if hasattr(block, 'text'):
                text_parts.append(block.text)
        return "\n".join(text_parts)

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
