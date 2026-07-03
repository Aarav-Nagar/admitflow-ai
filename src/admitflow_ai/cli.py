from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationTask:
    school: str
    task: str
    due: str


def sample_tasks() -> list[ApplicationTask]:
    return [
        ApplicationTask("Example University", "Draft personal statement", "2026-10-15"),
        ApplicationTask("Example Tech", "Request recommendation", "2026-09-30"),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="Print sample tasks.")
    args = parser.parse_args()

    if args.sample:
        for task in sample_tasks():
            print(f"{task.due} | {task.school} | {task.task}")


if __name__ == "__main__":
    main()

