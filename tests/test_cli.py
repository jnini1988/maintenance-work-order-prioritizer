from pathlib import Path

from work_order_prioritizer.cli import run


def test_run_returns_markdown_report_for_sample_data():
    report = run("data/sample_work_orders.csv")

    assert "# Maintenance Work Order Priority Report" in report
    assert "- Valid work orders: 7" in report
    assert "- Skipped rows: 2" in report
    assert "WO-1004" in report
    assert "Fuel leak investigation" in report


def test_run_writes_report_to_output_file(tmp_path: Path):
    output_path = tmp_path / "priority_report.md"

    report = run("data/sample_work_orders.csv", str(output_path))

    assert output_path.exists()
    saved_report = output_path.read_text(encoding="utf-8")
    assert saved_report == report
    assert "# Maintenance Work Order Priority Report" in saved_report