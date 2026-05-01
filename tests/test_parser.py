import pytest

from work_order_prioritizer.parser import (
    parse_float_in_range,
    parse_int_in_range,
    parse_row,
    parse_work_orders_from_rows,
)


def valid_row() -> dict[str, str]:
    return {
        "work_order_id": "WO-1",
        "asset": "Pump-1",
        "description": "Inspect seal",
        "likelihood": "0.75",
        "impact": "4",
        "downtime_hours": "2.5",
        "safety_critical": "8",
        "age_days": "7",
    }


def test_parse_row_returns_work_order_for_valid_input():
    order = parse_row(valid_row())

    assert order.work_order_id == "WO-1"
    assert order.asset == "Pump-1"
    assert order.description == "Inspect seal"
    assert order.likelihood == 0.75
    assert order.impact == 4
    assert order.downtime_hours == 2.5
    assert order.safety_critical == 8
    assert order.age_days == 7


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("work_order_id", ""),
        ("asset", ""),
        ("description", ""),
        ("likelihood", "-0.1"),
        ("likelihood", "1.1"),
        ("impact", "0"),
        ("impact", "6"),
        ("downtime_hours", "-1"),
        ("safety_critical", "-1"),
        ("safety_critical", "11"),
        ("age_days", "-3"),
    ],
)
def test_parse_row_rejects_invalid_fields(field: str, bad_value: str):
    row = valid_row()
    row[field] = bad_value

    with pytest.raises(ValueError):
        parse_row(row)


@pytest.mark.parametrize("bad_value", ["-0.1", "1.1"])
def test_parse_float_in_range_rejects_invalid_likelihood(bad_value: str):
    with pytest.raises(ValueError):
        parse_float_in_range(bad_value, "likelihood", 0.0, 1.0)


@pytest.mark.parametrize("bad_value", ["0", "6"])
def test_parse_int_in_range_rejects_invalid_impact(bad_value: str):
    with pytest.raises(ValueError):
        parse_int_in_range(bad_value, "impact", 1, 5)


@pytest.mark.parametrize("bad_value", ["-1", "11"])
def test_parse_int_in_range_rejects_invalid_safety_critical(bad_value: str):
    with pytest.raises(ValueError):
        parse_int_in_range(bad_value, "safety_critical", 0, 10)


@pytest.mark.parametrize("bad_value", ["-1", "-0.5"])
def test_parse_float_in_range_rejects_invalid_downtime_hours(bad_value: str):
    with pytest.raises(ValueError):
        parse_float_in_range(bad_value, "downtime_hours", 0.0, 1000.0)


@pytest.mark.parametrize("bad_value", ["-1", "-5"])
def test_parse_int_in_range_rejects_invalid_age_days(bad_value: str):
    with pytest.raises(ValueError):
        parse_int_in_range(bad_value, "age_days", 0, 10000)


def test_parse_work_orders_from_rows_skips_bad_rows():
    good = valid_row()
    bad = valid_row()
    bad["asset"] = ""

    valid_orders, warnings = parse_work_orders_from_rows([good, bad])

    assert len(valid_orders) == 1
    assert len(warnings) == 1
    assert "Skipped line 3" in warnings[0]
    assert "asset is required" in warnings[0]