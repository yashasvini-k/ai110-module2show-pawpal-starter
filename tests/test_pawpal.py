import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Fixtures ---

@pytest.fixture
def sample_task():
    return Task(name="Walk", duration_minutes=20, priority=3)

@pytest.fixture
def sample_pet():
    return Pet(name="Biscuit", species="Dog", age=3)

@pytest.fixture
def owner_with_pet(sample_pet):
    owner = Owner(name="Alex", available_minutes_per_day=60)
    owner.add_pet(sample_pet)
    return owner, sample_pet


# --- Original tests ---

def test_mark_complete_changes_status(sample_task):
    """mark_complete() should set completed to True."""
    sample_task.mark_complete()
    assert sample_task.completed is True

def test_adding_task_increases_pet_task_count(sample_pet):
    """Adding a task should increase the pet's task list by 1."""
    initial = len(sample_pet.get_tasks())
    sample_pet.add_task(Task(name="Feeding", duration_minutes=10, priority=4))
    assert len(sample_pet.get_tasks()) == initial + 1

def test_invalid_priority_raises_error():
    """Priority outside 1–5 should raise ValueError."""
    with pytest.raises(ValueError):
        Task(name="Bad task", duration_minutes=10, priority=9)

def test_completed_task_is_not_schedulable(sample_task):
    """A completed task should not be schedulable regardless of time available."""
    sample_task.mark_complete()
    assert sample_task.is_schedulable(999) is False

def test_scheduler_respects_time_budget(owner_with_pet):
    """Scheduler must not schedule more minutes than the owner has available."""
    owner, pet = owner_with_pet
    pet.add_task(Task(name="Walk",     duration_minutes=20, priority=5))
    pet.add_task(Task(name="Play",     duration_minutes=20, priority=3))
    pet.add_task(Task(name="Grooming", duration_minutes=30, priority=1))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    total = sum(t.duration_minutes for t, _ in scheduler.scheduled_tasks)
    assert total <= owner.get_available_time()


# --- Sorting tests ---

def test_sort_by_time_orders_correctly(owner_with_pet):
    """sort_by_time() should return tasks in ascending HH:MM order."""
    owner, pet = owner_with_pet
    pet.add_task(Task(name="Afternoon walk", duration_minutes=20, priority=3, start_time="14:00"))
    pet.add_task(Task(name="Morning meds",   duration_minutes=5,  priority=5, start_time="08:00"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    sorted_tasks = scheduler.sort_by_time()
    times = [t.start_time for t, _ in sorted_tasks if t.start_time]
    assert times == sorted(times)


# --- Filtering tests ---

def test_filter_by_pet_returns_correct_tasks(owner_with_pet):
    """filter_by_pet() should only return tasks for the named pet."""
    owner, pet = owner_with_pet
    pet.add_task(Task(name="Walk", duration_minutes=20, priority=3))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    results = scheduler.filter_by_pet("Biscuit")
    assert all(t.name == "Walk" for t in results)

def test_filter_by_status_incomplete(owner_with_pet):
    """filter_by_status(False) should return only incomplete tasks."""
    owner, pet = owner_with_pet
    pet.add_task(Task(name="Walk", duration_minutes=20, priority=3))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    incomplete = scheduler.filter_by_status(completed=False)
    assert all(not t.completed for t, _ in incomplete)


# --- Recurring task tests ---

def test_recurring_task_creates_next_occurrence(sample_pet):
    """Completing a recurring task should add a new task to the pet."""
    task = Task(name="Walk", duration_minutes=20, priority=3,
                is_recurring=True, frequency="daily")
    sample_pet.add_task(task)
    owner = Owner(name="Alex", available_minutes_per_day=60, pets=[sample_pet])
    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    initial_count = len(sample_pet.get_tasks())
    scheduler.complete_task(task, sample_pet)
    assert len(sample_pet.get_tasks()) == initial_count + 1

def test_recurring_task_next_due_date_is_tomorrow(sample_pet):
    """A daily recurring task's next occurrence should be due tomorrow."""
    today = date.today()
    task = Task(name="Walk", duration_minutes=20, priority=3,
                is_recurring=True, frequency="daily", due_date=today)
    sample_pet.add_task(task)
    owner = Owner(name="Alex", available_minutes_per_day=60, pets=[sample_pet])
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    scheduler.complete_task(task, sample_pet)

    next_task = sample_pet.get_tasks()[-1]
    assert next_task.due_date == today + timedelta(days=1)


# --- Conflict detection tests ---

def test_conflict_detected_for_same_start_time(owner_with_pet):
    """Two tasks at the same start_time should trigger a conflict warning."""
    owner, pet = owner_with_pet
    pet.add_task(Task(name="Walk",    duration_minutes=20, priority=5, start_time="08:00"))
    pet.add_task(Task(name="Feeding", duration_minutes=10, priority=4, start_time="08:00"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) >= 1

def test_no_conflict_for_different_times(owner_with_pet):
    """Tasks at different start times should not trigger any conflict warnings."""
    owner, pet = owner_with_pet
    pet.add_task(Task(name="Walk",    duration_minutes=20, priority=5, start_time="07:00"))
    pet.add_task(Task(name="Feeding", duration_minutes=10, priority=4, start_time="08:00"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    assert scheduler.detect_conflicts() == []