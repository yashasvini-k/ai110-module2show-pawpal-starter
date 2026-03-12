import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Fixtures ---

@pytest.fixture
def sample_task():
    return Task(name="Walk", duration_minutes=20, priority=3)

@pytest.fixture
def sample_pet():
    return Pet(name="Biscuit", species="Dog", age=3)

@pytest.fixture
def sample_owner(sample_pet):
    owner = Owner(name="Alex", available_minutes_per_day=60)
    owner.add_pet(sample_pet)
    return owner


# --- Tests ---

def test_mark_complete_changes_status(sample_task):
    """mark_complete() should set completed to True."""
    assert sample_task.completed is False
    sample_task.mark_complete()
    assert sample_task.completed is True

def test_adding_task_increases_pet_task_count(sample_pet):
    """Adding a task to a pet should increase its task list by 1."""
    initial_count = len(sample_pet.get_tasks())
    sample_pet.add_task(Task(name="Feeding", duration_minutes=10, priority=4))
    assert len(sample_pet.get_tasks()) == initial_count + 1

def test_invalid_priority_raises_error():
    """Task with priority outside 1-5 should raise ValueError."""
    with pytest.raises(ValueError):
        Task(name="Bad task", duration_minutes=10, priority=9)

def test_completed_task_is_not_schedulable(sample_task):
    """A completed task should not be schedulable."""
    sample_task.mark_complete()
    assert sample_task.is_schedulable(999) is False

def test_scheduler_respects_time_budget(sample_owner):
    """Scheduler should not exceed the owner's available minutes."""
    pet = sample_owner.pets[0]
    pet.add_task(Task(name="Walk",     duration_minutes=20, priority=5))
    pet.add_task(Task(name="Play",     duration_minutes=20, priority=3))
    pet.add_task(Task(name="Grooming", duration_minutes=30, priority=1))

    scheduler = Scheduler(sample_owner)
    scheduler.generate_plan()

    total = sum(t.duration_minutes for t, _ in scheduler.scheduled_tasks)
    assert total <= sample_owner.get_available_time()