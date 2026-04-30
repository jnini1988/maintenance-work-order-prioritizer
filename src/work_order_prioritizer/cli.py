import argparse
from pathlib import Path
from typing import Optional

from work_order_prioritizer.parser import parse_work_orders
from work_order_prioritizer.report import generate_markdown_report
from work_order_prioritizer.scoring import prioritize_work_orders


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Prioritize maintenance work orders from a CSV file."
    )
    parser.add_argument(
        "input_csv",
        help="Path to the work order CSV file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path to write the Markdown report.",
    )
    return parser


def run(input_csv: str, output: Optional[str] = None) -> str:
    """Run the prioritization pipeline and return the generated report."""
    work_orders, warnings = parse_work_orders(input_csv)
    prioritized_orders = prioritize_work_orders(work_orders)
    report = generate_markdown_report(prioritized_orders, warnings)

    if output is not None:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")

    return report


def main() -> int:
    """Entry point for the command-line interface."""
    args = build_parser().parse_args()
    report = run(args.input_csv, args.output)

    if args.output is None:
        print(report)
    else:
        print(f"Wrote report to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())