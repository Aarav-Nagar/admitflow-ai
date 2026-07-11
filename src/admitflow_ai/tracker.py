from __future__ import annotations

from datetime import date

from .models import (
    ApplicationStatus,
    DeadlineAlert,
    Requirement,
    RequirementStatus,
    SchoolApplication,
)


def sample_applications() -> list[SchoolApplication]:
    return [
        SchoolApplication(
            school="Example University",
            round_name="Early Action",
            program="Computer Science",
            portal_url="https://admissions.example.edu/apply",
            status=ApplicationStatus.DRAFTING,
            requirements=(
                Requirement(
                    "Draft personal statement",
                    date(2026, 10, 15),
                    RequirementStatus.IN_PROGRESS,
                    notes="Keep draft local until final review.",
                ),
                Requirement(
                    "Request counselor transcript",
                    date(2026, 9, 20),
                    RequirementStatus.MISSING,
                    owner="counselor",
                ),
                Requirement(
                    "Activities list",
                    date(2026, 10, 1),
                    RequirementStatus.COMPLETE,
                ),
            ),
        ),
        SchoolApplication(
            school="Example Tech",
            round_name="Regular Decision",
            program="AI and Society",
            portal_url="https://apply.example-tech.edu",
            status=ApplicationStatus.RESEARCHING,
            requirements=(
                Requirement(
                    "Request recommendation",
                    date(2026, 9, 30),
                    RequirementStatus.MISSING,
                    owner="teacher",
                ),
                Requirement(
                    "Portfolio short answer",
                    date(2026, 11, 15),
                    RequirementStatus.MISSING,
                ),
            ),
        ),
    ]


def build_deadline_alerts(
    applications: list[SchoolApplication],
    *,
    today: date,
    horizon_days: int = 45,
) -> list[DeadlineAlert]:
    alerts: list[DeadlineAlert] = []
    for application in applications:
        for requirement in application.open_requirements():
            days_until_due = (requirement.due - today).days
            if days_until_due > horizon_days:
                continue
            alerts.append(
                DeadlineAlert(
                    school=application.school,
                    requirement=requirement.name,
                    due=requirement.due,
                    days_until_due=days_until_due,
                    status=requirement.status,
                    priority=_priority(days_until_due),
                )
            )

    return sorted(alerts, key=lambda alert: (alert.due, alert.school, alert.requirement))


def _priority(days_until_due: int) -> str:
    if days_until_due < 0:
        return "overdue"
    if days_until_due <= 7:
        return "urgent"
    if days_until_due <= 21:
        return "soon"
    return "watch"


def privacy_notes() -> tuple[str, ...]:
    return (
        "Store applicant names, essays, recommendation details, and portal credentials outside source control.",
        "Run AI review prompts on redacted essay snippets unless the student explicitly opts in to sharing more context.",
        "Keep the local tracker useful without requiring cloud sync, analytics, or third-party admissions accounts.",
    )
