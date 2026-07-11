from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class ApplicationStatus(str, Enum):
    RESEARCHING = "researching"
    DRAFTING = "drafting"
    READY_TO_SUBMIT = "ready_to_submit"
    SUBMITTED = "submitted"


class RequirementStatus(str, Enum):
    MISSING = "missing"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


@dataclass(frozen=True)
class Requirement:
    name: str
    due: date
    status: RequirementStatus = RequirementStatus.MISSING
    owner: str = "student"
    notes: str = ""

    @property
    def is_complete(self) -> bool:
        return self.status == RequirementStatus.COMPLETE


@dataclass(frozen=True)
class SchoolApplication:
    school: str
    round_name: str
    program: str
    portal_url: str
    status: ApplicationStatus
    requirements: tuple[Requirement, ...] = field(default_factory=tuple)

    def open_requirements(self) -> tuple[Requirement, ...]:
        return tuple(item for item in self.requirements if not item.is_complete)

    def next_deadline(self) -> Requirement | None:
        open_items = self.open_requirements()
        if not open_items:
            return None
        return min(open_items, key=lambda item: item.due)


@dataclass(frozen=True)
class DeadlineAlert:
    school: str
    requirement: str
    due: date
    days_until_due: int
    status: RequirementStatus
    priority: str

    def as_row(self) -> dict[str, str | int]:
        return {
            "school": self.school,
            "requirement": self.requirement,
            "due": self.due.isoformat(),
            "days_until_due": self.days_until_due,
            "status": self.status.value,
            "priority": self.priority,
        }
