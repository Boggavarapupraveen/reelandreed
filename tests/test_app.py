from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_renders_without_exceptions():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=240)
    app.run()
    assert not app.exception, [f"{exc.type}: {exc.message}" for exc in app.exception]
    assert [tab.label for tab in app.tabs] == ["Overview", "Model comparison", "Language lab", "Corpus"]
    pills = app.get("pills")
    assert len(pills) == 1
    assert len(pills[0].options) == 4
    assert len(app.dataframe) >= 1
    assert len(app.get("plotly_chart")) >= 8


def test_selecting_another_film_updates_the_dashboard():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=240)
    app.run()
    pills = app.get("pills")[0]
    rrr_label = [option for option in pills.options if option.startswith("RRR")]
    assert rrr_label
    pills.set_value(rrr_label[0]).run()
    assert not app.exception, [f"{exc.type}: {exc.message}" for exc in app.exception]
    body = " ".join(element.value for element in app.markdown if isinstance(element.value, str))
    assert "RRR" in body
