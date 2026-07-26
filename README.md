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
- Essay versions by school prompt, reviewer, draft status, update date, and
  word count.
- School-specific checklists that merge application requirements with missing
  or in-progress supplemental essays.
- Local-first privacy guidance for essays, recommendation details, and portal
  credentials.

## Quick Start

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
python -m admitflow_ai --sample --today 2026-09-15
python -m admitflow_ai --sample --today 2026-09-15 --format json
python -m admitflow_ai --essay-versions
python -m admitflow_ai --checklist-school "Example University" --today 2026-09-15
python -m admitflow_ai --privacy-notes
```

Sample table output:

```text
2026-09-20 | URGENT  | Example University | Request counselor transcript | missing
2026-09-30 | SOON    | Example Tech | Request recommendation | missing
2026-10-15 | WATCH   | Example University | Draft personal statement | in_progress
```

Essay version output:

```text
2026-09-14 | Example University | Personal statement | v2 | ready_for_review | 622 words
2026-09-10 | Example Tech | Portfolio short answer | v1 | outline | 238 words
```

School checklist output:

```text
2026-09-20 | URGENT  | requirement | Request counselor transcript | missing | application requirement
2026-09-20 | HIGH    | essay | Essay: Personal statement | in_progress | example-university/personal-statement/v2
2026-09-20 | HIGH    | essay | Essay: Why computer science at Example University? | missing | school prompt
2026-10-01 | SOON    | requirement | Activities list | complete | application requirement
2026-10-15 | WATCH   | requirement | Draft personal statement | in_progress | application requirement
```

## Data Model

`SchoolApplication` groups the student-facing admissions context with the
requirements that still need work. `Requirement` records each deadline and
completion status. `build_deadline_alerts()` filters completed items, applies a
configurable due-date horizon, and returns stable rows for CLIs, tests, or future
UI views.

Day 10 adds `EssayVersion` and `ChecklistItem`. `latest_essay_versions()` keeps
the newest draft per school prompt, while `generate_school_checklist()` turns a
school profile into a deterministic checklist that highlights incomplete essays
without storing essay text in the repository.

## Privacy Notes

- Keep applicant names, essays, recommendation details, and portal credentials
  outside source control.
- Redact essay snippets before using optional AI review prompts.
- Prefer local files and explicit exports over background cloud sync for this
  starter project.
