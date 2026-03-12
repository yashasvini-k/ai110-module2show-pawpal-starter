from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    preferences: str = "none"  # e.g. "morning", "evening", "none"

    def get_available_time(self) -> int:
        """Returns how many minutes per day the owner has available for pet care."""
        return self.available_minutes_per_day


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: Optional[str] = None  # e.g. "requires medication"

    def get_profile(self) -> dict:
        """Returns a summary of the pet's info for display or scheduling context."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "special_needs": self.special_needs,
        }


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int  # 1 (low) to 5 (high)
    preferred_time: str = "any"  # "morning", "afternoon", "evening", or "any"
    is_recurring: bool = False
    completed: bool = False

    def __post_init__(self):
        """Validates that priority is between 1 and 5."""
        if not (1 <= self.priority <= 5):
            raise ValueError(f"Priority must be between 1 and 5, got {self.priority}")

    def mark_complete(self) -> None:
        """Marks the task as completed."""
        self.completed = True

    def is_schedulable(self, available_minutes: int) -> bool:
        """Returns True if the task can fit within the available time."""
        return self.duration_minutes <= available_minutes


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks
        self.scheduled_tasks: list[Task] = []
        self.unscheduled_tasks: list[Task] = []

    def generate_plan(self) -> None:
        """Sorts tasks by priority and fits them into the owner's available time."""
        pass

    def get_summary(self) -> str:
        """Returns a human-readable plan with basic reasoning."""
        pass

    def reset(self) -> None:
        """Clears the current scheduled and unscheduled task lists."""
        pass