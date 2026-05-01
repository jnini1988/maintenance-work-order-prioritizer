from work_order_prioritizer.models import PrioritizedWorkOrder, WorkOrder


def compute_priority_score(order: WorkOrder) -> float:
    """Compute a transparent priority score for a validated work order."""
    return (
        order.likelihood * order.impact
        + order.safety_critical
        + order.age_days * 0.1
    )


def assign_priority_level(score: float) -> str:
    """Convert a numeric priority score into a priority level."""
    if score >= 15:
        return "Critical"
    if score >= 10:
        return "High"
    if score >= 5:
        return "Medium"
    return "Low"


def prioritize_work_orders(orders: list[WorkOrder]) -> list[PrioritizedWorkOrder]:
    """Return work orders sorted from highest to lowest priority."""
    prioritized = [
        PrioritizedWorkOrder(
            work_order=order,
            score=compute_priority_score(order),
            level=assign_priority_level(compute_priority_score(order)),
        )
        for order in orders
    ]

    return sorted(
        prioritized,
        key=lambda item: (-item.score, item.work_order.work_order_id),
    )