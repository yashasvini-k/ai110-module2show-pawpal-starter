from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes_per_day=60, preferences="morning")

dog = Pet(name="Biscuit", species="Dog", age=3)
cat = Pet(name="Mochi", species="Cat", age=5, special_needs="requires medication")

# --- Add tasks to dog ---
dog.add_task(Task(name="Morning walk",      duration_minutes=20, priority=5, preferred_time="morning", is_recurring=True))
dog.add_task(Task(name="Feeding",           duration_minutes=10, priority=4, preferred_time="morning", is_recurring=True))
dog.add_task(Task(name="Fetch / play",      duration_minutes=15, priority=2, preferred_time="afternoon"))

# --- Add tasks to cat ---
cat.add_task(Task(name="Administer meds",   duration_minutes=5,  priority=5, preferred_time="morning", is_recurring=True))
cat.add_task(Task(name="Feeding",           duration_minutes=10, priority=4, preferred_time="morning", is_recurring=True))
cat.add_task(Task(name="Grooming session",  duration_minutes=20, priority=3, preferred_time="evening"))

# --- Register pets with owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- Run scheduler ---
scheduler = Scheduler(owner)
scheduler.generate_plan()
print(scheduler.get_summary())