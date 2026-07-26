from datetime import date

from admitflow_ai.models import EssayStatus, EssayVersion, RequirementStatus
from admitflow_ai.tracker import (
    build_deadline_alerts,
    generate_school_checklist,
    latest_essay_versions,
    privacy_notes,
    sample_applications,
    sample_essay_versions,
)


def test_sample_applications_include_deadlines_and_portals() -> None:
    applications = sample_applications()

    assert all(application.portal_url for application in applications)
    assert all(application.requirements for application in applications)
    assert all(application.supplemental_prompts for application in applications)
    assert all(requirement.due for application in applications for requirement in application.requirements)


def test_deadline_alerts_skip_completed_items_and_sort_by_due_date() -> None:
    alerts = build_deadline_alerts(
        sample_applications(),
        today=date(2026, 9, 15),
        horizon_days=45,
    )

    assert [alert.due for alert in alerts] == sorted(alert.due for alert in alerts)
    assert {alert.status for alert in alerts} <= {
        RequirementStatus.MISSING,
        RequirementStatus.IN_PROGRESS,
    }
    assert "Activities list" not in {alert.requirement for alert in alerts}


def test_deadline_alert_priorities_are_deterministic() -> None:
    alerts = build_deadline_alerts(
        sample_applications(),
        today=date(2026, 9, 15),
        horizon_days=120,
    )
    priorities = {alert.requirement: alert.priority for alert in alerts}

    assert priorities["Request counselor transcript"] == "urgent"
    assert priorities["Request recommendation"] == "soon"
    assert priorities["Portfolio short answer"] == "watch"


def test_privacy_notes_warn_about_sensitive_data() -> None:
    notes = " ".join(privacy_notes()).lower()

    assert "source control" in notes
    assert "redacted" in notes


def test_latest_essay_versions_keep_newest_school_prompt_pair() -> None:
    latest = latest_essay_versions(sample_essay_versions())
    rows = {(item.school, item.prompt): item for item in latest}

    personal_statement = rows[("Example University", "Personal statement")]

    assert personal_statement.version == 2
    assert personal_statement.status == EssayStatus.READY_FOR_REVIEW
    assert personal_statement.version_id == "example-university/personal-statement/v2"
    assert rows[("Example Tech", "Portfolio short answer")].version == 1


def test_latest_essay_versions_use_updated_date_as_tiebreaker() -> None:
    versions = [
        EssayVersion(
            school="Example University",
            prompt="Personal statement",
            version=2,
            updated_on=date(2026, 9, 1),
            word_count=600,
            status=EssayStatus.DRAFTING,
        ),
        EssayVersion(
            school="Example University",
            prompt="Personal statement",
            version=2,
            updated_on=date(2026, 9, 3),
            word_count=620,
            status=EssayStatus.READY_FOR_REVIEW,
        ),
    ]

    assert latest_essay_versions(versions)[0].updated_on == date(2026, 9, 3)


def test_school_checklist_combines_requirements_and_essay_statuses() -> None:
    application = sample_applications()[0]
    checklist = generate_school_checklist(
        application,
        essay_versions=sample_essay_versions(),
        today=date(2026, 9, 15),
    )
    rows = {item.task: item for item in checklist}

    assert rows["Request counselor transcript"].category == "requirement"
    assert rows["Request counselor transcript"].priority == "urgent"
    assert rows["Essay: Personal statement"].status == RequirementStatus.IN_PROGRESS
    assert rows["Essay: Personal statement"].source == "example-university/personal-statement/v2"
    assert rows["Essay: Why computer science at Example University?"].status == RequirementStatus.MISSING


def test_final_essay_version_marks_checklist_item_complete() -> None:
    application = sample_applications()[1]
    checklist = generate_school_checklist(
        application,
        essay_versions=[
            EssayVersion(
                school="Example Tech",
                prompt="Community impact statement",
                version=3,
                updated_on=date(2026, 9, 22),
                word_count=392,
                status=EssayStatus.FINAL,
            )
        ],
        today=date(2026, 9, 15),
    )
    rows = {item.task: item for item in checklist}

    assert rows["Essay: Community impact statement"].status == RequirementStatus.COMPLETE
    assert rows["Essay: Community impact statement"].source == "example-tech/community-impact-statement/v3"
