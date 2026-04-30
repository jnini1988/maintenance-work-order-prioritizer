import pytest

from work_order_prioritizer.parser import (
    parse_bool,
    parse_row,
    parse_work_orders_from_rows,
)


def valid_row() -> dict[str, str]:
    return {
        "work_order_id": "WO-1",
        "asset": "Pump-1",
        "description": "Inspect seal",
        "likelihood": "3",
        "impact": "4",
        "downtime_hours": "2.5",
        "safety_critical": "yes",
        "age_days": "7",
    }


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("yes", True),
        ("Y", True),
        ("true", True),
        ("1", True),
        ("no", False),
        ("N", False),
        ("false", False),
        ("0", False),
    ],
)
def test_parse_bool_accepts_expected_values(raw_value: str, expected: bool):
    assert parse_bool(raw_value) is expected


def test_parse_bool_rejects_invalid_value():
    with pytest.raises(ValueError):
        parse_bool("maybe")


def test_parse_row_returns_work_order_for_valid_input():
    order = parse_row(valid_row())

    assert order.work_order_id == "WO-1"
    assert order.asset == "Pump-1"
    assert order.description == "Inspect seal"
    assert order.likelihood == 3
    assert order.impact == 4
    assert order.downtime_hours == 2.5
    assert order.safety_critical is True
    assert order.age_days == 7


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("work_order_id", ""),
        ("asset", ""),
        ("description", ""),
        ("likelihood", "0"),
        ("likelihood", "6"),
        ("impact", "0"),
        ("impact", "6"),
        ("downtime_hours", "-1"),
        ("age_days", "-3"),
        ("safety_critical", "maybe"),
    ],
)
def test_parse_row_rejects_invalid_fields(field: str, bad_value: str):
    row = valid_row()
    row[field] = bad_value

    with pytest.raises(ValueError):
        parse_row(row)


def test_parse_work_orders_from_rows_skips_bad_rows():
    good = valid_row()
    bad = valid_row()
    bad["asset"] = ""

    valid_orders, warnings = parse_work_orders_from_rows([good, bad])

    assert len(valid_orders) == 1
    assert len(warnings) == 1
    assert "Skipped line 3" in warnings[0]
    assert "asset is required" in warnings[0]