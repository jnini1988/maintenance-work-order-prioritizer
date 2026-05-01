from work_order_prioritizer.models import PrioritizedWorkOrder, WorkOrder
from work_order_prioritizer.report import generate_markdown_report


def make_prioritized_order() -> PrioritizedWorkOrder:
    order = WorkOrder(
        work_order_id="WO-1",
        asset="Pump",
        description="Inspect seal",
        likelihood=0.5,
        impact=4,
        safety_critical=0,
        age_days=5,
    )
    return PrioritizedWorkOrder(work_order=order, score=2.5, level="Low")


def test_generate_markdown_report_includes_summary_and_ranked_order():
    prioritized_orders = [make_prioritized_order()]

    report = generate_markdown_report(prioritized_orders)

    assert "# Maintenance Work Order Priority Report" in report
    assert "- Valid work orders: 1" in report
    assert "- Skipped rows: 0" in report
    assert "| 1 | WO-1 | Pump | Low | 2.5 | Inspect seal |" in report


def test_generate_markdown_report_includes_priority_counts():
    prioritized_orders = [make_prioritized_order()]

    report = generate_markdown_report(prioritized_orders)

    assert "- Critical: 0" in report
    assert "- High: 0" in report
    assert "- Medium: 0" in report
    assert "- Low: 1" in report


def test_generate_markdown_report_handles_empty_valid_orders():
    report = generate_markdown_report([])

    assert "- Valid work orders: 0" in report
    assert "No valid work orders were found." in report


def test_generate_markdown_report_includes_warnings():
    report = generate_markdown_report([], ["Skipped line 2: asset is required"])

    assert "- Skipped rows: 1" in report
    assert "## Warnings" in report
    assert "- Skipped line 2: asset is required" in report