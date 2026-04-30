# Maintenance Work Order Prioritizer

A Python command-line tool that reads maintenance work orders from a CSV file, validates each row, computes a priority score, assigns a priority level, and generates a Markdown report.

## Problem

Maintenance teams often need to decide which work orders should be handled first. This project provides a simple way to rank work orders based on likelihood, impact, downtime, safety criticality, and age.

## Planned Features

- Read work orders from CSV
- Validate malformed rows
- Compute priority scores
- Assign priority levels
- Generate a Markdown report
- Include unit tests and CI checks
- Document AI collaboration prompts and review decisions

## Input Format

The input CSV will include:

```text
work_order_id,asset,description,likelihood,impact,downtime_hours,safety_critical,age_days
```

## Setup

Clone the repository and install the required Python packages.

```bash
git clone https://github.com/jnini1988/maintenance-work-order-prioritizer.git
cd maintenance-work-order-prioritizer

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
