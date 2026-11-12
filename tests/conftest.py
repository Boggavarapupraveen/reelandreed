"""Test configuration: keep the fast, offline path for the suite."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["SENTIMENT_DISABLE_TRANSFORMER"] = "1"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
os.environ.setdefault("HF_HOME", str(ROOT / ".cache" / "huggingface"))

from src import runtime  # noqa: E402

runtime.configure()
