from __future__ import annotations

import argparse
import json
from datetime import date

from .tracker import (
    build_deadline_alerts,
    generate_school_checklist,
    latest_essay_versions,
    privacy_notes,
    sample_applications,
    sample_essay_versions,
)


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
    parser.add_argument(
        "--essay-versions",
        action="store_true",
        help="Print the latest tracked essay version for each school prompt.",
    )
    parser.add_argument(
        "--checklist-school",
        help="Print a generated checklist for one sample school.",
    )
    args = parser.parse_args()

    applications = sample_applications()
    essays = sample_essay_versions()

    if args.privacy_notes:
        for index, note in enumerate(privacy_notes(), start=1):
            print(f"{index}. {note}")

    if args.sample:
        alerts = build_deadline_alerts(
            applications,
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

    if args.essay_versions:
        latest = latest_essay_versions(essays)
        if args.format == "json":
            print(json.dumps([version.as_row() for version in latest], indent=2))
        else:
            for version in latest:
                print(
                    f"{version.updated_on.isoformat()} | {version.school} | "
                    f"{version.prompt} | v{version.version} | "
                    f"{version.status.value} | {version.word_count} words"
                )

    if args.checklist_school:
        application = _find_school(applications, args.checklist_school)
        checklist = generate_school_checklist(
            application,
            essay_versions=essays,
            today=date.fromisoformat(args.today),
        )
        if args.format == "json":
            print(json.dumps([item.as_row() for item in checklist], indent=2))
        else:
            for item in checklist:
                due = item.due.isoformat() if item.due else "no due date"
                print(
                    f"{due} | {item.priority.upper():7} | {item.category} | "
                    f"{item.task} | {item.status.value} | {item.source}"
                )


def _find_school(applications, school_name: str):
    for application in applications:
        if application.school.casefold() == school_name.casefold():
            return application
    choices = ", ".join(application.school for application in applications)
    raise SystemExit(f"Unknown school '{school_name}'. Available: {choices}")


if __name__ == "__main__":
    main()
