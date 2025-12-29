#!/usr/bin/env python3
"""
Initial setup script for the Insurance Aggregator PoC.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    print("=" * 60)
    print("Insurance Aggregator PoC - Setup")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 10):
        print("Error: Python 3.10+ required")
        sys.exit(1)

    print(f"\n✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Install dependencies
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    print("✓ Dependencies installed")

    # Install Playwright browsers
    print("\n🌐 Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✓ Playwright browsers installed")
    except Exception as e:
        print(f"⚠ Playwright install failed: {e}")
        print("  (Quote automation will use mock data)")

    # Create directories
    print("\n📁 Creating directories...")
    dirs = [
        "data/products",
        "data/documents/sunlife",
        "data/documents/manulife",
        "data/documents/canadalife",
        "data/vectors"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✓ Directories created")

    # Check for API key
    print("\n🔑 Checking API key...")
    if os.getenv("ANTHROPIC_API_KEY"):
        print("✓ ANTHROPIC_API_KEY found")
    else:
        print("⚠ ANTHROPIC_API_KEY not set")
        print("  Set it with: export ANTHROPIC_API_KEY=your_key_here")

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Set ANTHROPIC_API_KEY if not already set")
    print("  2. Run: streamlit run ui/app.py")
    print("  3. Or run: python main.py (for CLI)")
    print()


if __name__ == "__main__":
    main()
