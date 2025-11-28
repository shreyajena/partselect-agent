# app/config/__init__.py
# Re-export settings from parent config.py for backward compatibility
import sys
import importlib.util
from pathlib import Path

# Import settings from parent config.py (not this directory)
parent_dir = Path(__file__).parent.parent
config_file = parent_dir / "config.py"

spec = importlib.util.spec_from_file_location("parent_config", config_file)
parent_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent_config_module)

settings = parent_config_module.settings

__all__ = ["settings"]

