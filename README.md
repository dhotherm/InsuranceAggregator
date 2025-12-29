# Insurance Aggregator PoC

**AI-native insurance comparison demonstrating the "aggregator threat"**

## The Strategic Point

This proof-of-concept demonstrates how trivially an AI-powered interface can abstract away insurance carriers (Sun Life, Manulife, Canada Life), owning the customer relationship while the carriers become commoditized "dumb pipes."

**The question isn't IF this will happen. It's whether Sun Life builds it first.**

## Quick Start

```bash
# 1. Setup
python scripts/setup.py

# 2. Set API key
export ANTHROPIC_API_KEY=your_key_here

# 3. Run the demo
streamlit run ui/app.py
```

## Demo Scenarios

1. **Life Stage Analysis**: "I'm 38, married with two kids, just bought a house..."
2. **Quote Comparison**: "Get me term life quotes from all three carriers..."
3. **Coverage Gap Analysis**: "I have X coverage, what am I missing?"
4. **Policy Deep Dive**: "What's NOT covered by Sun Life vs Manulife?"

## Architecture

```
┌─────────────────────────────────────────┐
│           ORCHESTRATOR                   │
│        (Claude reasoning)                │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐
│Research│ │ Quote │ │ Docs  │
│ Agent │ │ Agent │ │ Agent │
└───────┘ └───────┘ └───────┘
    │         │         │
    ▼         ▼         ▼
 Products   Quotes   Policy
  (JSON)    (Mock)   (RAG)
```

## The Aggregator Threat Model

```
Customer → AI Aggregator → [Sun Life | Manulife | Canada Life]
              ↑
        Owns relationship
        Owns data
        Owns experience
```

Carriers become interchangeable utilities. Margin compression follows.

## Files

- `agents/` - AI agents (orchestrator, research, quotes, documents)
- `data/products/` - Product catalog JSON files
- `ui/app.py` - Streamlit demo interface
- `main.py` - CLI interface

## For the Executive Demo

See `demo/demo_script.md` for the 15-minute presentation flow.

Key talking points:
- 30 seconds vs 30 minutes
- No forms filled out
- AI knows products better than advisors
- Who owns the customer relationship?
