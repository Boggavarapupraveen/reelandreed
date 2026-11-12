"""Print a reproducible summary of the five-film ensemble.

Usage:
    python scripts/model_report.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import runtime

runtime.configure()

from src.config import FILM_TITLES  # noqa: E402
from src.sentiment import analyze_title  # noqa: E402


def main() -> None:
    print(f"{'Film':30} {'Verdict':9} {'Score':>6} {'Conf':>6} {'Stars':>6} {'Agree':>6}  Review split")
    print("-" * 92)
    for title in FILM_TITLES:
        bundle = analyze_title(title, include_transformer=True)
        split = bundle.frame["fused_label"].value_counts().to_dict()
        print(
            f"{title:30} {bundle.overall_label:9} {bundle.overall_score_100:6.1f} "
            f"{bundle.confidence * 100:5.0f}% {bundle.star_average:6.2f} "
            f"{bundle.pairwise_agreement * 100:5.0f}%  {split}"
        )
        for name, summary in bundle.models.items():
            print(f"  - {name:16} {summary.label:9} {summary.score_100:5.1f}  ({summary.confidence * 100:.0f}% conf.)")
        print(f"  note: {bundle.transformer_note}")
        print()


if __name__ == "__main__":
    main()
