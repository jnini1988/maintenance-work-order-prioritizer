import pytest

from work_order_prioritizer.models import WorkOrder
from work_order_prioritizer.scoring import (
    assign_priority_level,
    compute_priority_score,
    prioritize_work_orders,
)


def make_order(
    work_order_id: str,
    likelihood: int,
    impact: int,
    downtime_hours: float,
    safety_critical: bool,
    age_days: int,
) -> WorkOrder:
    return WorkOrder(
        work_order_id=work_order_id,
        asset="Pump",
        description="Test work order",
        likelihood=likelihood,
        impact=impact,
        downtime_hours=downtime_hours,
        safety_critical=safety_critical,
        age_days=age_days,
    )


def test_compute_priority_score_includes_all_factors():
    order = make_order(
        work_order_id="WO-1",
        likelihood=5,
        impact=5,
        downtime_hours=8,
        safety_critical=True,
        age_days=10,
    )

    score = compute_priority_score(order)

    assert score == pytest.approx(40.0)


@pytest.mark.parametrize(
    ("score", "expected_level"),
    [
        (35, "Critical"),
        (34.9, "High"),
        (25, "High"),
        (24.9, "Medium"),
        (15, "Medium"),
        (14.9, "Low"),
    ],
)
def test_assign_priority_level_thresholds(score: float, expected_level: str):
    assert assign_priority_level(score) == expected_level


def test_prioritize_work_orders_sorts_highest_score_first():
    low = make_order("WO-LOW", 1, 1, 0, False, 0)
    high = make_order("WO-HIGH", 5, 5, 8, True, 10)
    middle = make_order("WO-MID", 3, 4, 2, False, 5)

    prioritized = prioritize_work_orders([low, high, middle])

    assert [item.work_order.work_order_id for item in prioritized] == [
        "WO-HIGH",
        "WO-MID",
        "WO-LOW",
    ]


def test_prioritize_work_orders_breaks_score_ties_by_work_order_id():
    first = make_order("WO-1", 3, 3, 0, False, 0)
    second = make_order("WO-2", 3, 3, 0, False, 0)

    prioritized = prioritize_work_orders([second, first])

    assert [item.work_order.work_order_id for item in prioritized] == ["WO-1", "WO-2"]