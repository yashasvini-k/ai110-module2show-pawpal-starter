# PawPal+ Project Reflection

## 1. System Design

- Set Up Their Pet Profile
- Manage Care Tasks
- Generate and View Today's Plan


**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I designed four classes. Owner holds the user's constraints like available time and preferences. Pet stores the animal's profile including any special needs. Task is the core unit, which holds care activity details like duration, priority, and preferred time of day. Scheduler is the orchestrator: it takes the owner, pet, and task list and produces a filtered, prioritized daily plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

### Change 1: Simplified Scheduler constructor
**Original design:** `Scheduler.__init__()` accepted three arguments — `owner`, `pet`, and `tasks`.

**What changed:** Reduced it to accept only `owner`.

**Why:** The `Owner` already holds a list of `Pet` objects, and each `Pet` already holds 
its own `Task` list. Passing all three separately was redundant — the scheduler can 
walk the chain `owner → pets → tasks` on its own using `owner.get_all_tasks()`. 
This makes creating a scheduler much simpler: `Scheduler(owner)` instead of 
`Scheduler(owner, pet, tasks)`.

---

### Change 2: Added `tasks` list to `Pet`
**Original design:** `Pet` only held profile info (name, species, age, special_needs).

**What changed:** Added a `tasks` list attribute and `add_task()` / `get_tasks()` methods to `Pet`.

**Why:** Tasks need to belong to a specific pet, not just float in a general list. 
Attaching tasks directly to a pet makes the data model more accurate and lets the 
scheduler know which pet each task belongs to.

---

### Change 3: Added `pets` list to `Owner`
**Original design:** `Owner` only held personal constraints (name, available time, preferences).

**What changed:** Added a `pets` list and `add_pet()` method to `Owner`.

**Why:** For the scheduler to retrieve all tasks through the owner, the owner needs 
to know about their pets. This is the key link in the chain that makes the 
simplified `Scheduler` constructor possible.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Conflict detection only flags tasks with the exact same start_time string. It does not check whether two tasks overlap in duration (e.g. a 30-min task at 08:00 and a 10-min task at 08:15 would not be flagged). This keeps the logic simple and readable but means partial overlaps go undetected. A more accurate approach would convert times to minutes-since-midnight and compare ranges, but adds complexity not needed for this version.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
