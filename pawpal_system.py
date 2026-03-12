from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """Represents a single pet care activity."""
    name: str
    duration_minutes: int
    priority: int                       # 1 (low) to 5 (high)
    preferred_time: str = "any"         # "morning", "afternoon", "evening", or "any"
    is_recurring: bool = False
    frequency: str = "daily"            # "daily" or "weekly" (only used if is_recurring=True)
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    start_time: Optional[str] = None    # "HH:MM" format, e.g. "08:00"

    def __post_init__(self):
        """Validates that priority is between 1 and 5."""
        if not (1 <= self.priority <= 5):
            raise ValueError(f"Priority must be between 1 and 5, got {self.priority}")

    def mark_complete(self) -> Optional["Task"]:
        """Marks the task as completed and returns the next occurrence if recurring."""
        self.completed = True
        if self.is_recurring:
            delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
            return Task(
                name=self.name,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                preferred_time=self.preferred_time,
                is_recurring=self.is_recurring,
                frequency=self.frequency,
                due_date=self.due_date + delta,
                start_time=self.start_time,
            )
        return None

    def is_schedulable(self, available_minutes: int) -> bool:
        """Returns True if the task fits within the available time and is not completed."""
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
    preferences: str = "any"
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

    # ------------------------------------------------------------------
    # Core plan generation
    # ------------------------------------------------------------------

    def generate_plan(self) -> None:
        """Sorts tasks by priority and fits them into the owner's available time."""
        self.scheduled_tasks = []
        self.unscheduled_tasks = []
        time_remaining = self.owner.get_available_time()

        all_pairs = [
            (task, pet)
            for pet in self.owner.pets
            for task in pet.get_tasks()
        ]

        # Sort by priority descending (5 = highest first)
        all_pairs.sort(key=lambda x: x[0].priority, reverse=True)

        for task, pet in all_pairs:
            if task.is_schedulable(time_remaining):
                self.scheduled_tasks.append((task, pet))
                time_remaining -= task.duration_minutes
            else:
                self.unscheduled_tasks.append((task, pet))

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def sort_by_time(self) -> list[tuple[Task, Pet]]:
        """Returns scheduled tasks sorted by start_time (HH:MM). Tasks with no
        start_time are placed at the end."""
        def time_key(pair: tuple[Task, Pet]) -> str:
            t = pair[0].start_time
            return t if t is not None else "99:99"

        return sorted(self.scheduled_tasks, key=time_key)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Returns all scheduled tasks that belong to the named pet."""
        return [
            task for task, pet in self.scheduled_tasks
            if pet.name.lower() == pet_name.lower()
        ]

    def filter_by_status(self, completed: bool) -> list[tuple[Task, Pet]]:
        """Returns scheduled tasks filtered by completion status."""
        return [
            (task, pet) for task, pet in self.scheduled_tasks
            if task.completed == completed
        ]

    # ------------------------------------------------------------------
    # Recurring task handling
    # ------------------------------------------------------------------

    def complete_task(self, task: Task, pet: Pet) -> None:
        """Marks a task complete and re-adds the next occurrence to the pet if recurring."""
        next_task = task.mark_complete()
        if next_task:
            pet.add_task(next_task)

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """Checks for tasks whose start times overlap and returns warning strings.

        A conflict is when two scheduled tasks share the same HH:MM start_time.
        Tasks without a start_time are skipped.
        """
        warnings = []
        timed_tasks = [
            (task, pet) for task, pet in self.scheduled_tasks
            if task.start_time is not None
        ]

        # Compare every pair once
        for i in range(len(timed_tasks)):
            for j in range(i + 1, len(timed_tasks)):
                t1, p1 = timed_tasks[i]
                t2, p2 = timed_tasks[j]
                if t1.start_time == t2.start_time:
                    warnings.append(
                        f"⚠️  Conflict at {t1.start_time}: "
                        f"'{t1.name}' ({p1.name}) and '{t2.name}' ({p2.name})"
                    )
        return warnings

    # ------------------------------------------------------------------
    # Summary output
    # ------------------------------------------------------------------

    def get_summary(self) -> str:
        """Returns a formatted daily plan with conflict warnings and reasoning."""
        if not self.scheduled_tasks and not self.unscheduled_tasks:
            return "No plan generated yet. Run generate_plan() first."

        lines = []
        lines.append("=" * 45)
        lines.append("        🐾 PawPal+ — Today's Schedule")
        lines.append("=" * 45)
        lines.append(f"Owner : {self.owner.name}")
        lines.append(f"Budget: {self.owner.get_available_time()} mins\n")

        # Use time-sorted view for display
        sorted_plan = self.sort_by_time()
        if sorted_plan:
            lines.append("✅ Scheduled Tasks (sorted by time):")
            for task, pet in sorted_plan:
                time_str = f" @ {task.start_time}" if task.start_time else ""
                pref = f" [{task.preferred_time}]" if task.preferred_time != "any" else ""
                lines.append(
                    f"  • [{pet.name}]{time_str} {task.name}{pref}"
                    f" — {task.duration_minutes} min  (priority {task.priority})"
                )

        if self.unscheduled_tasks:
            lines.append("\n⚠️  Couldn't Fit (not enough time):")
            for task, pet in self.unscheduled_tasks:
                lines.append(
                    f"  • [{pet.name}] {task.name}"
                    f" — {task.duration_minutes} min  (priority {task.priority})"
                )

        # Conflict warnings
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\n🚨 Conflicts Detected:")
            lines.extend(f"  {w}" for w in conflicts)

        total = sum(t.duration_minutes for t, _ in self.scheduled_tasks)
        lines.append(f"\nTotal time scheduled: {total} mins")
        lines.append("=" * 45)
        return "\n".join(lines)

    def reset(self) -> None:
        """Clears the current plan so generate_plan() can be re-run."""
        self.scheduled_tasks = []
        self.unscheduled_tasks = []