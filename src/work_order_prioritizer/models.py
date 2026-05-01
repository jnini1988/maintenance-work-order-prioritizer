from dataclasses import dataclass


@dataclass(frozen=True)
class WorkOrder:
    """A validated maintenance work order."""

    work_order_id: str
    asset: str
    description: str
    likelihood: float
    impact: int
    safety_critical: int
    age_days: int


@dataclass(frozen=True)
class PrioritizedWorkOrder:
    """A work order with computed priority information."""

    work_order: WorkOrder
    score: float
    level: str