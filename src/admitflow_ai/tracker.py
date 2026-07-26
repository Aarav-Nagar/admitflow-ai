from __future__ import annotations

from datetime import date

from .models import (
    ApplicationStatus,
    ChecklistItem,
    DeadlineAlert,
    EssayStatus,
    EssayVersion,
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
            supplemental_prompts=(
                "Personal statement",
                "Why computer science at Example University?",
            ),
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
            supplemental_prompts=(
                "Portfolio short answer",
                "Community impact statement",
            ),
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


def sample_essay_versions() -> list[EssayVersion]:
    return [
        EssayVersion(
            school="Example University",
            prompt="Personal statement",
            version=1,
            updated_on=date(2026, 9, 8),
            word_count=548,
            status=EssayStatus.DRAFTING,
            reviewer="student",
            notes="Initial values-focused draft.",
        ),
        EssayVersion(
            school="Example University",
            prompt="Personal statement",
            version=2,
            updated_on=date(2026, 9, 14),
            word_count=622,
            status=EssayStatus.READY_FOR_REVIEW,
            reviewer="counselor",
            notes="Redacted copy ready for counselor feedback.",
        ),
        EssayVersion(
            school="Example Tech",
            prompt="Portfolio short answer",
            version=1,
            updated_on=date(2026, 9, 10),
            word_count=238,
            status=EssayStatus.OUTLINE,
            reviewer="student",
        ),
    ]


def latest_essay_versions(versions: list[EssayVersion]) -> list[EssayVersion]:
    latest_by_prompt: dict[tuple[str, str], EssayVersion] = {}
    for version in versions:
        key = (version.school.casefold(), version.prompt.casefold())
        current = latest_by_prompt.get(key)
        if current is None or (version.version, version.updated_on) > (
            current.version,
            current.updated_on,
        ):
            latest_by_prompt[key] = version

    return sorted(
        latest_by_prompt.values(),
        key=lambda item: (-item.updated_on.toordinal(), item.school, item.prompt),
    )


def generate_school_checklist(
    application: SchoolApplication,
    *,
    essay_versions: list[EssayVersion] | None = None,
    today: date | None = None,
) -> list[ChecklistItem]:
    essay_versions = essay_versions or []
    today = today or date.today()
    latest_essays = {
        (item.school.casefold(), item.prompt.casefold()): item
        for item in latest_essay_versions(essay_versions)
    }
    items: list[ChecklistItem] = []

    for requirement in application.requirements:
        items.append(
            ChecklistItem(
                school=application.school,
                category="requirement",
                task=requirement.name,
                due=requirement.due,
                status=requirement.status,
                owner=requirement.owner,
                source="application requirement",
                priority=_priority((requirement.due - today).days),
            )
        )

    for prompt in application.supplemental_prompts:
        latest = latest_essays.get((application.school.casefold(), prompt.casefold()))
        if latest is None:
            status = RequirementStatus.MISSING
            source = "school prompt"
        elif latest.status == EssayStatus.FINAL:
            status = RequirementStatus.COMPLETE
            source = latest.version_id
        else:
            status = RequirementStatus.IN_PROGRESS
            source = latest.version_id

        next_deadline = application.next_deadline()
        items.append(
            ChecklistItem(
                school=application.school,
                category="essay",
                task=f"Essay: {prompt}",
                due=next_deadline.due if next_deadline else None,
                status=status,
                owner="student",
                source=source,
                priority="high" if status != RequirementStatus.COMPLETE else "normal",
            )
        )

    return sorted(
        items,
        key=_checklist_sort_key,
    )


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


def _checklist_sort_key(item: ChecklistItem) -> tuple[date, int, str]:
    category_rank = {"requirement": 0, "essay": 1}
    return (
        item.due or date.max,
        category_rank.get(item.category, 99),
        item.task,
    )


def privacy_notes() -> tuple[str, ...]:
    return (
        "Store applicant names, essays, recommendation details, and portal credentials outside source control.",
        "Run AI review prompts on redacted essay snippets unless the student explicitly opts in to sharing more context.",
        "Keep the local tracker useful without requiring cloud sync, analytics, or third-party admissions accounts.",
    )
