from __future__ import annotations

import argparse
import json
from datetime import date

from .tracker import build_deadline_alerts, privacy_notes, sample_applications


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Track local-first college application deadlines."
    )
    parser.add_argument("--sample", action="store_true", help="Print sample deadline alerts.")
    parser.add_argument(
        "--today",
        default=date.today().isoformat(),
        help="Reference date for urgency calculations, in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--horizon-days",
        type=int,
        default=45,
        help="Only include open requirements due within this many days.",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Output format for sample deadline alerts.",
    )
    parser.add_argument(
        "--privacy-notes",
        action="store_true",
        help="Print local-first privacy guidance.",
    )
    args = parser.parse_args()

    if args.privacy_notes:
        for index, note in enumerate(privacy_notes(), start=1):
            print(f"{index}. {note}")

    if args.sample:
        alerts = build_deadline_alerts(
            sample_applications(),
            today=date.fromisoformat(args.today),
            horizon_days=args.horizon_days,
        )
        if args.format == "json":
            print(json.dumps([alert.as_row() for alert in alerts], indent=2))
        else:
            for alert in alerts:
                print(
                    f"{alert.due.isoformat()} | {alert.priority.upper():7} | "
                    f"{alert.school} | {alert.requirement} | {alert.status.value}"
                )


if __name__ == "__main__":
    main()
