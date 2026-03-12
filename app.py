import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

# -------------------------------------------------------
# Step 1: Page config
# -------------------------------------------------------
st.set_page_config(page_title="PawPal+", page_icon="🐾")
st.title("🐾 PawPal+")
st.caption("Your daily pet care planner")

# -------------------------------------------------------
# Step 2: Session state — the app's "memory"
# This block only runs once. After that, the owner object
# persists in st.session_state across every re-run.
# -------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None  # not set up yet

# -------------------------------------------------------
# Section A: Owner Setup
# -------------------------------------------------------
st.header("1. Owner Setup")

with st.form("owner_form"):
    owner_name = st.text_input("Your name")
    available_mins = st.number_input(
        "Minutes available for pet care today", min_value=5, max_value=480, value=60
    )
    preferences = st.selectbox(
        "Preferred time of day", ["any", "morning", "afternoon", "evening"]
    )
    submitted = st.form_submit_button("Save Owner")

if submitted and owner_name:
    # Create a fresh Owner but keep any existing pets if owner was already set
    existing_pets = st.session_state.owner.pets if st.session_state.owner else []
    st.session_state.owner = Owner(
        name=owner_name,
        available_minutes_per_day=int(available_mins),
        preferences=preferences,
        pets=existing_pets,
    )
    st.success(f"Owner saved: {owner_name}")

# Guard: nothing below works without an owner
if not st.session_state.owner:
    st.info("👆 Fill in your details above to get started.")
    st.stop()

owner = st.session_state.owner  # convenient shorthand

# -------------------------------------------------------
# Section B: Add a Pet
# -------------------------------------------------------
st.header("2. Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    special_needs = st.text_input("Special needs (optional)", placeholder="e.g. requires medication")
    add_pet = st.form_submit_button("Add Pet")

if add_pet and pet_name:
    # Prevent duplicate pet names
    existing_names = [p.name.lower() for p in owner.pets]
    if pet_name.lower() in existing_names:
        st.warning(f"A pet named '{pet_name}' already exists.")
    else:
        new_pet = Pet(
            name=pet_name,
            species=species,
            age=int(age),
            special_needs=special_needs if special_needs else None,
        )
        owner.add_pet(new_pet)  # <-- wired to your Owner method
        st.success(f"Added {species}: {pet_name}!")

# Show current pets
if owner.pets:
    st.subheader("Your pets")
    for pet in owner.pets:
        profile = pet.get_profile()  # <-- wired to your Pet method
        needs = f" — ⚠️ {profile['special_needs']}" if profile["special_needs"] else ""
        st.write(f"**{profile['name']}** ({profile['species']}, age {profile['age']}){needs}")
else:
    st.info("No pets added yet.")

# -------------------------------------------------------
# Section C: Add a Task
# -------------------------------------------------------
st.header("3. Add a Care Task")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Assign task to", pet_names)
        task_name = st.text_input("Task name", placeholder="e.g. Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=120, value=15)
        priority = st.slider("Priority", min_value=1, max_value=5, value=3)
        preferred_time = st.selectbox("Preferred time", ["any", "morning", "afternoon", "evening"])
        is_recurring = st.checkbox("Recurring daily task")
        add_task = st.form_submit_button("Add Task")

    if add_task and task_name:
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        new_task = Task(
            name=task_name,
            duration_minutes=int(duration),
            priority=priority,
            preferred_time=preferred_time,
            is_recurring=is_recurring,
        )
        target_pet.add_task(new_task)  # <-- wired to your Pet method
        st.success(f"Task '{task_name}' added to {selected_pet_name}!")

    # Show all tasks per pet
    st.subheader("Current tasks")
    for pet in owner.pets:
        tasks = pet.get_tasks()
        if tasks:
            st.write(f"**{pet.name}**")
            for t in tasks:
                status = "✅" if t.completed else "⬜"
                st.write(f"  {status} {t.name} — {t.duration_minutes} min (priority {t.priority})")

# -------------------------------------------------------
# Section D: Generate the Daily Plan
# -------------------------------------------------------
st.header("4. Generate Today's Plan")

if st.button("Generate Plan 🗓️"):
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("Add some tasks first!")
    else:
        scheduler = Scheduler(owner)       # <-- wired to your Scheduler
        scheduler.generate_plan()
        st.session_state.last_plan = scheduler.get_summary()

if "last_plan" in st.session_state:
    st.code(st.session_state.last_plan, language=None)