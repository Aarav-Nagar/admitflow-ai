# AdmitFlow AI

AdmitFlow AI is a local-first college application organizer for deadlines,
requirements, and privacy-aware review workflows.

It is intentionally small: the starter version models school applications,
tracks open requirements by due date, and prints deterministic deadline alerts
without sending student data to a cloud service.

## What It Tracks

- School, program, admission round, portal URL, and application status.
- Requirement name, owner, due date, status, and private notes.
- Open deadline alerts sorted by due date with `overdue`, `urgent`, `soon`, and
  `watch` priority buckets.
- Local-first privacy guidance for essays, recommendation details, and portal
  credentials.

## Quick Start

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
python -m admitflow_ai --sample --today 2026-09-15
python -m admitflow_ai --sample --today 2026-09-15 --format json
python -m admitflow_ai --privacy-notes
```

Sample table output:

```text
2026-09-20 | URGENT  | Example University | Request counselor transcript | missing
2026-09-30 | SOON    | Example Tech | Request recommendation | missing
2026-10-15 | WATCH   | Example University | Draft personal statement | in_progress
```

## Data Model

`SchoolApplication` groups the student-facing admissions context with the
requirements that still need work. `Requirement` records each deadline and
completion status. `build_deadline_alerts()` filters completed items, applies a
configurable due-date horizon, and returns stable rows for CLIs, tests, or future
UI views.

## Privacy Notes

- Keep applicant names, essays, recommendation details, and portal credentials
  outside source control.
- Redact essay snippets before using optional AI review prompts.
- Prefer local files and explicit exports over background cloud sync for this
  starter project.
