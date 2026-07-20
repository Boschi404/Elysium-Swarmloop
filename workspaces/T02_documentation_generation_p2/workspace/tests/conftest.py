"""Pytest configuration for documentation task."""
import sys
from pathlib import Path

# Add workspace root to sys.path so `app.main` can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))
