"""Runtime bootstrap for the dashboard.

Import and call :func:`configure` before importing matplotlib, wordcloud, torch,
or transformers. It keeps all caches inside the project (important on locked-down
Windows machines) and fixes a Windows temp-directory quirk.
"""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / ".cache"
TMP_DIR = CACHE_DIR / "tmp"
MPL_DIR = CACHE_DIR / "matplotlib"
HF_DIR = CACHE_DIR / "huggingface"
MODEL_DIR = ROOT / "models" / "distilbert-sst-2"
DATA_PATH = ROOT / "data" / "reviews.csv"

_CONFIGURED = False


def _install_tempfile_shim() -> None:
    """Avoid Windows temp folders whose DACL only grants the OWNER RIGHTS SID."""
    if os.name != "nt":
        return
    if tempfile.mkdtemp.__module__ != "tempfile":
        return

    def mkdtemp(suffix: str | None = None, prefix: str | None = None, dir: str | None = None) -> str:
        base = dir if dir is not None else tempfile.gettempdir()
        name = f"{prefix or 'tmp'}{uuid.uuid4().hex}{suffix or ''}"
        path = os.path.join(base, name)
        os.makedirs(path, exist_ok=False)
        return os.path.abspath(path)

    tempfile.mkdtemp = mkdtemp  # type: ignore[assignment]


def configure() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    for folder in (CACHE_DIR, TMP_DIR, MPL_DIR, HF_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(MPL_DIR))
    os.environ.setdefault("HF_HOME", str(HF_DIR))
    os.environ.setdefault("TMPDIR", str(TMP_DIR))
    os.environ.setdefault("TMP", str(TMP_DIR))
    os.environ.setdefault("TEMP", str(TMP_DIR))
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    _install_tempfile_shim()
    _CONFIGURED = True
