import pytest

from work_order_prioritizer.models import WorkOrder
from work_order_prioritizer.scoring import (
    assign_priority_level,
    compute_priority_score,
    prioritize_work_orders,
)


def make_order(
    work_order_id: str,
    likelihood: float,
    impact: int,
    safety_critical: int,
    age_days: int,
) -> WorkOrder:
    return WorkOrder(
        work_order_id=work_order_id,
        asset="Pump",
        description="Test work order",
        likelihood=likelihood,
        impact=impact,
        safety_critical=safety_critical,
        age_days=age_days,
    )


def test_compute_priority_score_includes_all_factors():
    order = make_order(
        work_order_id="WO-1",
        likelihood=0.9,
        impact=5,
        safety_critical=10,
        age_days=10,
    )

    score = compute_priority_score(order)

    assert score == pytest.approx(15.0)


@pytest.mark.parametrize(
    ("score", "expected_level"),
    [
        (15, "Critical"),
        (14.9, "High"),
        (10, "High"),
        (9.9, "Medium"),
        (5, "Medium"),
        (4.9, "Low"),
    ],
)
def test_assign_priority_level_thresholds(score: float, expected_level: str):
    assert assign_priority_level(score) == expected_level


def test_prioritize_work_orders_sorts_highest_score_first():
    low = make_order("WOLOW", 0.1, 1, 0, 0)
    high = make_order("WOHIGH", 0.9, 5, 10, 10)
    middle = make_order("WOMID", 0.5, 4, 4, 5)

    prioritized = prioritize_work_orders([low, high, middle])

    assert [item.work_order.work_order_id for item in prioritized] == [
        "WOHIGH",
        "WOMID",
        "WOLOW",
    ]


def test_prioritize_work_orders_breaks_score_ties_by_work_order_id():
    first = make_order("WO1", 0.5, 4, 0, 0)
    second = make_order("WO2", 0.5, 4, 0, 0)

    prioritized = prioritize_work_orders([second, first])

    assert [item.work_order.work_order_id for item in prioritized] == ["WO1", "WO2"]