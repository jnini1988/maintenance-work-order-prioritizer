import csv
import re
from pathlib import Path
from typing import Iterable, Union

from work_order_prioritizer.models import WorkOrder

REQUIRED_COLUMNS = {
    "work_order_id",
    "asset",
    "description",
    "likelihood",
    "impact",
    "safety_critical",
    "age_days",
}

def parse_float_in_range(value: str, field_name: str, minimum: float, maximum: float) -> float:
    """Parse a float and validate that it is within an inclusive range."""
    parsed = float(value)
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}")
    return parsed

def parse_int_in_range(value: str, field_name: str, minimum: int, maximum: int) -> int:
    """Parse an integer and validate that it is within an inclusive range."""
    parsed = int(value)
    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}")
    return parsed

def parse_nonnegative_int(value: str, field_name: str) -> int:
    """Parse a nonnegative integer."""
    parsed = int(value)
    if parsed < 0:
        raise ValueError(f"{field_name} must be nonnegative")
    return parsed


def parse_row(row: dict[str, str]) -> WorkOrder:
    """Parse and validate one CSV row."""
    work_order_id = row["work_order_id"].strip()
    asset = row["asset"].strip()
    description = row["description"].strip()

    if not work_order_id:
        raise ValueError("work_order_id is required")
    if re.fullmatch(r"[A-Za-z0-9]+", work_order_id) is None:
        raise ValueError("work_order_id must be alphanumeric")
    if not asset:
        raise ValueError("asset is required")
    if re.fullmatch(r"[A-Za-z0-9]+", asset) is None:
        raise ValueError("asset must be alphanumeric")
    if not description:
        raise ValueError("description is required")
    if len(description) > 250:
        raise ValueError("description must be 250 characters or fewer")

    return WorkOrder(
        work_order_id=work_order_id,
        asset=asset,
        description=description,
        likelihood=parse_float_in_range(row["likelihood"], "likelihood", 0.0, 1.0),
        impact=parse_int_in_range(row["impact"], "impact", 1, 5),
        safety_critical=parse_int_in_range(row["safety_critical"], "safety_critical", 0, 10),
        age_days=parse_nonnegative_int(row["age_days"], "age_days"),
    )


def parse_work_orders(path: Union[str, Path]) -> tuple[list[WorkOrder], list[str]]:
    """Read work orders from a CSV file.

    Returns valid work orders and warning messages for skipped rows.
    """
    csv_path = Path(path)
    valid_orders: list[WorkOrder] = []
    warnings: list[str] = []
    seen_work_order_ids: set[str] = set()

    with csv_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            return [], ["CSV file is empty"]

        missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            return [], [f"CSV is missing required columns: {missing}"]

        for line_number, row in enumerate(reader, start=2):
            try:
                parsed_order = parse_row(row)
                if parsed_order.work_order_id in seen_work_order_ids:
                    warnings.append(
                        f"Skipped line {line_number}: work_order_id must be unique; "
                        f"duplicate {parsed_order.work_order_id!r}"
                    )
                    continue

                seen_work_order_ids.add(parsed_order.work_order_id)
                valid_orders.append(parsed_order)
            except (KeyError, TypeError, ValueError) as exc:
                warnings.append(f"Skipped line {line_number}: {exc}")

    return valid_orders, warnings


def parse_work_orders_from_rows(rows: Iterable[dict[str, str]]) -> tuple[list[WorkOrder], list[str]]:
    """Parse work orders from in-memory rows for testing."""
    valid_orders: list[WorkOrder] = []
    warnings: list[str] = []
    seen_work_order_ids: set[str] = set()

    for line_number, row in enumerate(rows, start=2):
        try:
            parsed_order = parse_row(row)
            if parsed_order.work_order_id in seen_work_order_ids:
                warnings.append(
                    f"Skipped line {line_number}: work_order_id must be unique; "
                    f"duplicate {parsed_order.work_order_id!r}"
                )
                continue

            seen_work_order_ids.add(parsed_order.work_order_id)
            valid_orders.append(parsed_order)
        except (KeyError, TypeError, ValueError) as exc:
            warnings.append(f"Skipped line {line_number}: {exc}")

    return valid_orders, warnings