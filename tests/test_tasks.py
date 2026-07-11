from datetime import date

from admitflow_ai.models import RequirementStatus
from admitflow_ai.tracker import build_deadline_alerts, privacy_notes, sample_applications


def test_sample_applications_include_deadlines_and_portals() -> None:
    applications = sample_applications()

    assert all(application.portal_url for application in applications)
    assert all(application.requirements for application in applications)
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
