"""Make tempfile.mkdtemp use inherited Windows permissions.

On this Windows host, ``tempfile.mkdtemp`` creates a directory whose DACL contains
only an OWNER RIGHTS entry. Some subprocesses and installers then cannot write into
their own freshly-created temp folder. This module is loaded only while installing
dependencies (via PYTHONPATH); it preserves mkdtemp's uniqueness without applying
the restrictive mode-0700 ACL.

Usage::

    $env:PYTHONPATH = "$PWD\\scripts\\pip_sitecustomize"
    python -m pip install --target .vendor -r requirements.txt
"""

from __future__ import annotations

import os
import tempfile
import uuid


def _mkdtemp(suffix: str | None = None, prefix: str | None = None, dir: str | None = None) -> str:
    base = dir if dir is not None else tempfile.gettempdir()
    name = f"{prefix or 'tmp'}{uuid.uuid4().hex}{suffix or ''}"
    path = os.path.join(base, name)
    os.makedirs(path, exist_ok=False)
    return os.path.abspath(path)


tempfile.mkdtemp = _mkdtemp
