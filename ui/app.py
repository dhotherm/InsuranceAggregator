"""
Streamlit-based demo interface for the Insurance Aggregator PoC.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import InsuranceOrchestrator

# Page config
st.set_page_config(
    page_title="Insurance Advisor - Demo",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        max-width: 1200px;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .threat-banner {
        background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .carrier-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        margin-right: 0.5rem;
    }
    .sunlife { background: #ffd700; color: #333; }
    .manulife { background: #00a758; color: white; }
    .canadalife { background: #d71920; color: white; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🛡️ Insurance Advisor")
st.caption("AI-powered insurance comparison across Sun Life, Manulife, and Canada Life")

# Threat model banner
st.markdown("""
<div class="threat-banner">
    <strong>⚠️ Strategic Demo: The Aggregator Threat</strong><br>
    This demonstrates how an AI-native interface could abstract away insurance providers,
    owning the customer relationship while carriers become commoditized utilities.
    <br><em>This is the threat model — or the opportunity if we build it first.</em>
</div>
""", unsafe_allow_html=True)

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    return InsuranceOrchestrator(data_dir="./data")

orchestrator = get_orchestrator()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Sidebar
with st.sidebar:
    st.header("🎯 Quick Demo Scenarios")

    st.markdown("**Click to load pre-built queries:**")

    if st.button("📊 Life Stage Analysis", use_container_width=True):
        st.session_state.pending_query = "I'm 38 years old, married with two kids. We just bought a house with a $500,000 mortgage. My household income is about $150,000. What insurance should I have?"

    if st.button("💰 Compare Term Life Quotes", use_container_width=True):
        st.session_state.pending_query = "Get me term life insurance quotes from all three carriers for $500,000 coverage. I'm 35, non-smoker, male."

    if st.button("🔍 Critical Illness Deep Dive", use_container_width=True):
        st.session_state.pending_query = "Compare critical illness insurance across Sun Life, Manulife and Canada Life. What conditions are covered by each? Any significant differences in coverage?"

    if st.button("📋 Policy Exclusions", use_container_width=True):
        st.session_state.pending_query = "What are the main exclusions in Sun Life's term life policy versus Manulife's? What wouldn't be covered?"

    if st.button("🎯 Coverage Gap Analysis", use_container_width=True):
        st.session_state.pending_query = "I currently have group life insurance through work ($200K) and basic health coverage. I'm 42, married, one child, rent an apartment. Income is $95,000. What am I missing?"

    st.divider()

    st.header("📈 Demo Stats")
    st.metric("Products Indexed", "12")
    st.metric("Carriers", "3")
    st.metric("Document Pages", "0 (mock mode)")

    st.divider()

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        orchestrator.clear_history()
        st.rerun()

    st.divider()

    st.markdown("""
    **The Point:**
    - No carrier websites visited
    - No forms filled out
    - 30 seconds vs 30 minutes
    - Who owns the customer?
    """)

# Main chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process pending query from button clicks
if st.session_state.pending_query:
    prompt = st.session_state.pending_query
    st.session_state.pending_query = None

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Researching across carriers..."):
            try:
                response = orchestrator.process(prompt)
                st.markdown(response)
            except Exception as e:
                response = f"Error: {str(e)}\n\nPlease check that ANTHROPIC_API_KEY is set in your environment."
                st.error(response)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

# Chat input
if prompt := st.chat_input("Ask about insurance products, get quotes, or analyze your coverage needs..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Researching across carriers..."):
            try:
                response = orchestrator.process(prompt)
                st.markdown(response)
            except Exception as e:
                response = f"Error: {str(e)}\n\nPlease check that ANTHROPIC_API_KEY is set in your environment."
                st.error(response)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.875rem;">
    <strong>Proof of Concept</strong> — Built to demonstrate platform disintermediation risk<br>
    All quotes are estimates. This is not financial advice.
</div>
""", unsafe_allow_html=True)
