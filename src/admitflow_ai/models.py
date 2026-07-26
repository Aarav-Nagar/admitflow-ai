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


class EssayStatus(str, Enum):
    OUTLINE = "outline"
    DRAFTING = "drafting"
    READY_FOR_REVIEW = "ready_for_review"
    FINAL = "final"


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
    supplemental_prompts: tuple[str, ...] = field(default_factory=tuple)

    def open_requirements(self) -> tuple[Requirement, ...]:
        return tuple(item for item in self.requirements if not item.is_complete)

    def next_deadline(self) -> Requirement | None:
        open_items = self.open_requirements()
        if not open_items:
            return None
        return min(open_items, key=lambda item: item.due)


@dataclass(frozen=True)
class EssayVersion:
    school: str
    prompt: str
    version: int
    updated_on: date
    word_count: int
    status: EssayStatus
    reviewer: str = "student"
    notes: str = ""

    @property
    def version_id(self) -> str:
        prompt_key = self.prompt.lower().replace(" ", "-")
        return f"{self.school.lower().replace(' ', '-')}/{prompt_key}/v{self.version}"

    def as_row(self) -> dict[str, str | int]:
        return {
            "school": self.school,
            "prompt": self.prompt,
            "version": self.version,
            "updated_on": self.updated_on.isoformat(),
            "word_count": self.word_count,
            "status": self.status.value,
            "reviewer": self.reviewer,
            "version_id": self.version_id,
        }


@dataclass(frozen=True)
class ChecklistItem:
    school: str
    category: str
    task: str
    status: RequirementStatus
    owner: str
    due: date | None = None
    source: str = "generated"
    priority: str = "normal"

    def as_row(self) -> dict[str, str]:
        return {
            "school": self.school,
            "category": self.category,
            "task": self.task,
            "status": self.status.value,
            "owner": self.owner,
            "due": self.due.isoformat() if self.due else "",
            "source": self.source,
            "priority": self.priority,
        }


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
