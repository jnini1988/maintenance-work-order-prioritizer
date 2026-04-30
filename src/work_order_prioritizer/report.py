from typing import Optional

from work_order_prioritizer.models import PrioritizedWorkOrder


def generate_markdown_report(
    prioritized_orders: list[PrioritizedWorkOrder],
    warnings: Optional[list[str]] = None,
) -> str:
    """Generate a Markdown report for prioritized maintenance work orders."""
    warnings = warnings or []

    lines = [
        "# Maintenance Work Order Priority Report",
        "",
        "## Summary",
        "",
        f"- Valid work orders: {len(prioritized_orders)}",
        f"- Skipped rows: {len(warnings)}",
        "",
    ]

    if prioritized_orders:
        critical_count = sum(1 for item in prioritized_orders if item.level == "Critical")
        high_count = sum(1 for item in prioritized_orders if item.level == "High")
        medium_count = sum(1 for item in prioritized_orders if item.level == "Medium")
        low_count = sum(1 for item in prioritized_orders if item.level == "Low")

        lines.extend(
            [
                "## Priority Counts",
                "",
                f"- Critical: {critical_count}",
                f"- High: {high_count}",
                f"- Medium: {medium_count}",
                f"- Low: {low_count}",
                "",
                "## Ranked Work Orders",
                "",
                "| Rank | Work Order | Asset | Level | Score | Description |",
                "|---:|---|---|---|---:|---|",
            ]
        )

        for rank, item in enumerate(prioritized_orders, start=1):
            order = item.work_order
            lines.append(
                f"| {rank} | {order.work_order_id} | {order.asset} | "
                f"{item.level} | {item.score:.1f} | {order.description} |"
            )
    else:
        lines.extend(
            [
                "## Ranked Work Orders",
                "",
                "No valid work orders were found.",
            ]
        )

    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            lines.append(f"- {warning}")

    lines.append("")
    return "\n".join(lines)