import pytest
from pathlib import Path

from work_order_prioritizer.parser import (
    parse_float_in_range,
    parse_int_in_range,
    parse_row,
    parse_work_orders,
    parse_work_orders_from_rows,
)


def valid_row() -> dict[str, str]:
    return {
        "work_order_id": "WO1",
        "asset": "Pump1",
        "description": "Inspect seal",
        "likelihood": "0.75",
        "impact": "4",
        "safety_critical": "8",
        "age_days": "7",
    }


def test_parse_row_returns_work_order_for_valid_input():
    order = parse_row(valid_row())

    assert order.work_order_id == "WO1"
    assert order.asset == "Pump1"
    assert order.description == "Inspect seal"
    assert order.likelihood == 0.75
    assert order.impact == 4
    assert order.safety_critical == 8
    assert order.age_days == 7


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("work_order_id", ""),
        ("work_order_id", "WO-1"),
        ("asset", ""),
        ("asset", "Pump-1"),
        ("description", ""),
        ("description", "x" * 251),
        ("likelihood", "-0.1"),
        ("likelihood", "1.1"),
        ("impact", "0"),
        ("impact", "6"),
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


def test_parse_work_orders_from_rows_skips_duplicate_work_order_ids():
    first = valid_row()
    second = valid_row()
    second["asset"] = "Pump2"

    valid_orders, warnings = parse_work_orders_from_rows([first, second])

    assert len(valid_orders) == 1
    assert len(warnings) == 1
    assert "work_order_id must be unique" in warnings[0]


def test_parse_row_accepts_boundary_values():
    row = valid_row()
    row["description"] = "x" * 250
    row["likelihood"] = "0.0"
    row["impact"] = "1"
    row["safety_critical"] = "0"
    row["age_days"] = "0"

    order = parse_row(row)

    assert order.description == "x" * 250
    assert order.likelihood == 0.0
    assert order.impact == 1
    assert order.safety_critical == 0
    assert order.age_days == 0


def test_parse_row_accepts_upper_boundary_values():
    row = valid_row()
    row["likelihood"] = "1.0"
    row["impact"] = "5"
    row["safety_critical"] = "10"

    order = parse_row(row)

    assert order.likelihood == 1.0
    assert order.impact == 5
    assert order.safety_critical == 10


@pytest.mark.parametrize("field", ["likelihood", "impact", "safety_critical", "age_days"])
def test_parse_row_rejects_non_numeric_values(field: str):
    row = valid_row()
    row[field] = "not-a-number"

    with pytest.raises(ValueError):
        parse_row(row)


def test_parse_work_orders_returns_warning_for_empty_csv(tmp_path: Path):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    valid_orders, warnings = parse_work_orders(csv_path)

    assert valid_orders == []
    assert warnings == ["CSV file is empty"]


def test_parse_work_orders_returns_warning_for_missing_required_columns(tmp_path: Path):
    csv_path = tmp_path / "missing_columns.csv"
    csv_path.write_text(
        "work_order_id,asset,description,likelihood,impact,safety_critical\n"
        "WO1,Pump1,Inspect seal,0.5,3,2\n",
        encoding="utf-8",
    )

    valid_orders, warnings = parse_work_orders(csv_path)

    assert valid_orders == []
    assert len(warnings) == 1
    assert "CSV is missing required columns" in warnings[0]
    assert "age_days" in warnings[0]


def test_parse_work_orders_skips_duplicate_ids_with_line_number(tmp_path: Path):
    csv_path = tmp_path / "duplicate.csv"
    csv_path.write_text(
        "work_order_id,asset,description,likelihood,impact,safety_critical,age_days\n"
        "WO1,Pump1,Inspect seal,0.5,3,2,10\n"
        "WO1,Pump2,Inspect bearing,0.4,2,1,5\n",
        encoding="utf-8",
    )

    valid_orders, warnings = parse_work_orders(csv_path)

    assert len(valid_orders) == 1
    assert valid_orders[0].work_order_id == "WO1"
    assert len(warnings) == 1
    assert warnings[0] == "Skipped line 3: work_order_id must be unique; duplicate 'WO1'"