# PawPal+ Project Reflection

## 1. System Design

- Set Up Their Pet Profile
- Manage Care Tasks
- Generate and View Today's Plan


**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I designed four classes to model the PawPal+ system.

**Owner** holds the user's scheduling constraints — their name, how many minutes
they have available per day, and their preferred time of day. It acts as the
entry point for the scheduler.

**Pet** stores the animal's profile (name, species, age, special needs) and owns
a list of care tasks. Attaching tasks directly to the pet makes the data model
more accurate than having a flat global task list.

**Task** is the core unit the scheduler works with. It holds everything needed
to rank and slot an activity: name, duration, priority (1–5), preferred time,
recurrence settings, completion status, due date, and an optional start time.

**Scheduler** is the orchestrator. It accepts only an Owner and navigates the
owner → pets → tasks chain to build a prioritized daily plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

### Change 1: Simplified Scheduler constructor
**Original:** `Scheduler.__init__()` accepted `owner`, `pet`, and `tasks` separately.  
**Changed to:** Accept only `owner`.  
**Why:** The Owner already holds pets, and each Pet holds its tasks. Passing all
three separately was redundant. The scheduler can walk the chain on its own,
making instantiation as simple as `Scheduler(owner)`.

---

### Change 2: Added `tasks` list to `Pet`
**Original:** Pet only held profile attributes.  
**Changed to:** Added `tasks: list[Task]`, `add_task()`, and `get_tasks()`.  
**Why:** Tasks need to belong to a specific pet. This lets the scheduler know
which pet each task is associated with and enables per-pet filtering.

---

### Change 3: Added `pets` list to `Owner`
**Original:** Owner only held personal constraints.  
**Changed to:** Added `pets: list[Pet]`, `add_pet()`, and `get_all_tasks()`.  
**Why:** This is the key link that makes the simplified Scheduler constructor
possible. The owner is the single source of truth for all scheduling data.

---

## Change 4: Added scheduling fields to `Task`
**Original:** Task had no `start_time`, `due_date`, or `frequency`.  
**Changed to:** Added `start_time` (HH:MM), `due_date` (date), and `frequency`
(daily/weekly).  
**Why:** Sorting by time and conflict detection both require `start_time`.
Recurring task renewal requires `due_date` and `frequency` to calculate the
next occurrence using `timedelta`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

### Tradeoff 1: Exact-match conflict detection
The `detect_conflicts()` method only flags tasks that share the **exact same
`start_time` string**. It does not detect partial overlaps — for example, a
30-minute task at 08:00 and a 10-minute task at 08:15 would not be flagged even
though they overlap in real time.

This keeps the logic simple and readable (a string comparison vs. converting
times to minute offsets and comparing ranges), which is appropriate for a
first version. A production scheduler would need range-based overlap detection.

### Tradeoff 2: Priority-only scheduling ignores preferred time
`generate_plan()` sorts entirely by priority and ignores `preferred_time` when
deciding what to include. A priority-5 evening task will be scheduled before a
priority-3 morning task even if the owner prefers mornings. Enforcing preferred
time would require a two-pass algorithm (first fill preferred time slots, then
fill remaining slots), which adds complexity not needed for this version.

### Tradeoff 3: No time-slot assignment
The scheduler decides *what* to include but does not assign *when* each task
should happen (unless the user manually sets a `start_time`). A real planner
would auto-assign start times based on duration and preferred time windows.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

AI was used across every phase of the project, but for different purposes at each stage. During design, I used it for brainstorming — asking what classes a pet scheduling app would need and what attributes each should hold. During implementation, I used it in edit/inline mode to flesh out specific methods like `generate_plan()` and `detect_conflicts()`. During testing, I used it to suggest edge cases I hadn't considered, such as a pet with no tasks or an owner with no pets at all.

- What kinds of prompts or questions were most helpful?

The most effective prompts were specific and scoped to one method or behavior at a time — for example, "how should `mark_complete()` return the next occurrence of a recurring task using timedelta?" produced a clean, targeted answer. Broad prompts like "improve my scheduler" produced suggestions that were harder to evaluate and often missed the design intent.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When asking for conflict detection logic, the AI initially suggested raising a Python exception when two tasks shared the same start time. I rejected this because it would crash plan generation rather than warn the user — a pet care app should surface problems gracefully, not stop working. I modified the approach to return a list of warning strings instead, which the UI then displays as `st.warning` banners. 

- How did you evaluate or verify what the AI suggested?

I verified the change by writing two tests: one that confirms a conflict is detected, and one that confirms no false positives appear when times are different.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

The test suite covers 24 behaviors across all four classes:
- Task completion, priority validation (1–5 range enforced), and schedulability
- Pet task list starting empty, growing correctly when tasks are added, and returning the right profile data
- Owner returning an empty task list when it has no pets, and correctly aggregating tasks across multiple pets
- Scheduler respecting the time budget, prioritizing high-priority tasks when time is tight, and clearing state on reset
- Sorting returning tasks in HH:MM order with untimed tasks placed last
- Filtering by pet name (including an unknown name returning empty) and by completion status
- Recurring tasks creating a new instance on completion with the correct due date for both daily (+1 day) and weekly (+7 days) frequencies
- Conflict detection flagging shared start times, passing on different times, and never flagging tasks that have no start time at all

- Why were these tests important?

These tests matter because the scheduler's value depends on correctness — if it silently drops a high-priority task or creates a duplicate recurring task, the owner loses trust in the tool immediately.


**b. Confidence**

- How confident are you that your scheduler works correctly?

Confidence level: ⭐⭐⭐⭐ (4/5)

The happy paths and the main edge cases are well covered. The known gap is overlapping duration detection — two tasks at 08:00 and 08:15 where the first runs 30 minutes overlap in real time but are not flagged, because the current logic only compares exact start time strings. 

- What edge cases would you test next if you had more time?

If I had more time, I would test: tasks that exactly fill the time budget to the minute, an owner with zero available minutes, a recurring task being completed multiple days in a row, and conflict detection across two different pets scheduled at the same time.


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The clearest win was the decision to simplify the `Scheduler` constructor to accept only an `Owner`. That single design choice made every other part of the system cleaner — the scheduler could walk `owner → pets → tasks` on its own, which eliminated redundant arguments and made the UI code much simpler to write. Getting that relationship right early made the rest of the build feel straightforward.


**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The conflict detection is the most obvious thing to redesign. Converting `start_time` strings to minutes-since-midnight and comparing ranges rather than exact strings would catch partial overlaps and make the feature genuinely useful. I would also add a second scheduling pass that respects `preferred_time` — right now a priority-5 evening task gets scheduled before a priority-3 morning task even if the owner prefers mornings, which doesn't reflect how a real day works.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that AI accelerates execution but does not replace intent. The AI could scaffold a class, suggest a sort key, or draft a test — but it had no idea that I wanted warnings instead of exceptions, or that the Scheduler should navigate through the Owner rather than receive a flat task list. Every design decision that made the system coherent came from a deliberate human choice. The lead architect's job is to hold the vision clearly enough to know when to accept an AI suggestion and when to override it.