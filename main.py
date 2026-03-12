from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes_per_day=90, preferences="morning")

dog = Pet(name="Biscuit", species="Dog", age=3)
cat = Pet(name="Mochi",   species="Cat", age=5, special_needs="requires medication")

# --- Tasks added OUT OF ORDER to test sorting ---
dog.add_task(Task(name="Fetch / play",    duration_minutes=15, priority=2,
                  preferred_time="afternoon", start_time="14:00"))
dog.add_task(Task(name="Morning walk",    duration_minutes=20, priority=5,
                  preferred_time="morning",   start_time="07:00",
                  is_recurring=True, frequency="daily"))
dog.add_task(Task(name="Feeding",         duration_minutes=10, priority=4,
                  preferred_time="morning",   start_time="08:00",
                  is_recurring=True, frequency="daily"))

cat.add_task(Task(name="Administer meds", duration_minutes=5,  priority=5,
                  preferred_time="morning",   start_time="08:00",   # <-- conflict with dog feeding
                  is_recurring=True, frequency="daily"))
cat.add_task(Task(name="Feeding",         duration_minutes=10, priority=4,
                  preferred_time="morning",   start_time="08:30",
                  is_recurring=True, frequency="daily"))
cat.add_task(Task(name="Grooming",        duration_minutes=20, priority=3,
                  preferred_time="evening",   start_time="18:00"))

owner.add_pet(dog)
owner.add_pet(cat)

# --- Generate and print plan ---
scheduler = Scheduler(owner)
scheduler.generate_plan()
print(scheduler.get_summary())

# --- Demo: filtering ---
print("\n--- Filter: Biscuit's tasks only ---")
for task in scheduler.filter_by_pet("Biscuit"):
    print(f"  • {task.name} ({task.duration_minutes} min)")

print("\n--- Filter: incomplete tasks ---")
for task, pet in scheduler.filter_by_status(completed=False):
    print(f"  • [{pet.name}] {task.name}")

# --- Demo: recurring task renewal ---
print("\n--- Completing 'Morning walk' (recurring) ---")
walk = next(t for t in dog.get_tasks() if t.name == "Morning walk")
scheduler.complete_task(walk, dog)
print(f"  walk.completed = {walk.completed}")
next_walk = dog.get_tasks()[-1]
print(f"  Next occurrence due: {next_walk.due_date}")