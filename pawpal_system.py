from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    """Represents a single pet care activity."""
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
        """Returns True if the task fits within the available time remaining."""
        return not self.completed and self.duration_minutes <= available_minutes


@dataclass
class Pet:
    """Stores a pet's profile and their list of care tasks."""
    name: str
    species: str
    age: int
    special_needs: Optional[str] = None
    tasks: list[Task] = field(default_factory=list)

    def get_profile(self) -> dict:
        """Returns a summary dict of the pet's info."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "special_needs": self.special_needs,
        }

    def add_task(self, task: Task) -> None:
        """Adds a care task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Returns all tasks assigned to this pet."""
        return self.tasks


@dataclass
class Owner:
    """Represents the pet owner and their scheduling constraints."""
    name: str
    available_minutes_per_day: int
    preferences: str = "any"  # "morning", "afternoon", "evening", or "any"
    pets: list[Pet] = field(default_factory=list)

    def get_available_time(self) -> int:
        """Returns how many minutes per day the owner has available."""
        return self.available_minutes_per_day

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet to the owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collects and returns all tasks across all of the owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """Retrieves tasks from the owner's pets and builds a prioritized daily plan."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled_tasks: list[tuple[Task, Pet]] = []
        self.unscheduled_tasks: list[tuple[Task, Pet]] = []

    def generate_plan(self) -> None:
        """Sorts tasks by priority and fits them into the owner's available time."""
        self.scheduled_tasks = []
        self.unscheduled_tasks = []
        time_remaining = self.owner.get_available_time()

        # Collect (task, pet) pairs so we know which pet each task belongs to
        all_pairs = []
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                all_pairs.append((task, pet))

        # Sort by priority descending (5 = highest first)
        all_pairs.sort(key=lambda x: x[0].priority, reverse=True)

        for task, pet in all_pairs:
            if task.is_schedulable(time_remaining):
                self.scheduled_tasks.append((task, pet))
                time_remaining -= task.duration_minutes
            else:
                self.unscheduled_tasks.append((task, pet))

    def get_summary(self) -> str:
        """Returns a formatted, human-readable daily plan with basic reasoning."""
        if not self.scheduled_tasks and not self.unscheduled_tasks:
            return "No plan generated yet. Run generate_plan() first."

        lines = []
        lines.append("=" * 40)
        lines.append("       🐾 PawPal+ — Today's Schedule")
        lines.append("=" * 40)
        lines.append(f"Owner : {self.owner.name}")
        lines.append(f"Budget: {self.owner.get_available_time()} mins\n")

        if self.scheduled_tasks:
            lines.append("✅ Scheduled Tasks:")
            for task, pet in self.scheduled_tasks:
                pref = f" [{task.preferred_time}]" if task.preferred_time != "any" else ""
                lines.append(
                    f"  • [{pet.name}] {task.name}{pref} "
                    f"— {task.duration_minutes} min  (priority {task.priority})"
                )

        if self.unscheduled_tasks:
            lines.append("\n⚠️  Couldn't Fit (not enough time):")
            for task, pet in self.unscheduled_tasks:
                lines.append(
                    f"  • [{pet.name}] {task.name} "
                    f"— {task.duration_minutes} min  (priority {task.priority})"
                )

        total = sum(t.duration_minutes for t, _ in self.scheduled_tasks)
        lines.append(f"\nTotal time scheduled: {total} mins")
        lines.append("=" * 40)
        return "\n".join(lines)

    def reset(self) -> None:
        """Clears the current plan so generate_plan() can be re-run."""
        self.scheduled_tasks = []
        self.unscheduled_tasks = []