#!/usr/bin/env python3
"""Compare hourly, daily, and hybrid GPU rental plans without hiding assumptions."""

import argparse
import json
import math


def nonnegative(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("expected a finite non-negative number")
    return number


def probability(value: str) -> float:
    number = nonnegative(value)
    if number > 1:
        raise argparse.ArgumentTypeError("probability must be between 0 and 1")
    return number


def calculate(args: argparse.Namespace) -> dict:
    fixed = args.api_cost + args.storage_cost
    total_hours = args.pilot_hours + args.formal_hours
    hourly = args.hourly_price * total_hours + fixed + args.reacquire_probability * args.reacquire_impact
    daily_units = math.ceil(total_hours / 24) if total_hours else 0
    formal_daily_units = math.ceil(args.formal_hours / 24) if args.formal_hours else 0
    daily = args.daily_price * daily_units + fixed
    hybrid = args.hourly_price * args.pilot_hours + args.daily_price * formal_daily_units + fixed
    plans = {"hourly": hourly, "daily": daily, "hybrid": hybrid}
    recommendation = min(plans, key=plans.get)
    return {
        "assumptions": {
            "hourly_price": args.hourly_price,
            "daily_price": args.daily_price,
            "pilot_hours": args.pilot_hours,
            "formal_hours": args.formal_hours,
            "api_cost": args.api_cost,
            "storage_cost": args.storage_cost,
            "reacquire_probability": args.reacquire_probability,
            "reacquire_impact": args.reacquire_impact,
        },
        "break_even_hours_without_capacity_risk": args.daily_price / args.hourly_price,
        "expected_cost": {name: round(value, 2) for name, value in plans.items()},
        "arithmetic_recommendation": recommendation,
        "decision_boundary": "Recheck availability, refund rules, deadline risk, and whether the formal workload is ready before purchase.",
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--hourly-price", type=nonnegative, required=True)
    result.add_argument("--daily-price", type=nonnegative, required=True)
    result.add_argument("--pilot-hours", type=nonnegative, default=0)
    result.add_argument("--formal-hours", type=nonnegative, required=True)
    result.add_argument("--api-cost", type=nonnegative, default=0)
    result.add_argument("--storage-cost", type=nonnegative, default=0)
    result.add_argument("--reacquire-probability", type=probability, default=0)
    result.add_argument("--reacquire-impact", type=nonnegative, default=0)
    return result


def main() -> None:
    args = parser().parse_args()
    if args.hourly_price == 0:
        raise SystemExit("--hourly-price must be greater than zero")
    print(json.dumps(calculate(args), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
