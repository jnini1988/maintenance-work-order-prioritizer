from dataclasses import dataclass


@dataclass(frozen=True)
class WorkOrder:
    """A validated maintenance work order."""

    work_order_id: str
    asset: str
    description: str
    likelihood: int
    impact: int
    downtime_hours: float
    safety_critical: bool
    age_days: int


@dataclass(frozen=True)
class PrioritizedWorkOrder:
    """A work order with computed priority information."""

    work_order: WorkOrder
    score: float
    level: str