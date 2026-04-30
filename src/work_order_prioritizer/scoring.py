from work_order_prioritizer.models import PrioritizedWorkOrder, WorkOrder


def compute_priority_score(order: WorkOrder) -> float:
    """Compute a transparent priority score for a work order."""
    safety_bonus = 10.0 if order.safety_critical else 0.0
    return (
        order.likelihood * order.impact
        + order.downtime_hours * 0.5
        + safety_bonus
        + order.age_days * 0.1
    )


def assign_priority_level(score: float) -> str:
    """Convert a numeric priority score into a priority level."""
    if score >= 35:
        return "Critical"
    if score >= 25:
        return "High"
    if score >= 15:
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