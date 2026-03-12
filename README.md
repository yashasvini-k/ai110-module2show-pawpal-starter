# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.


### Testing PawPal+


Run the full test suite with:

```bash
python3 -m pytest tests/ -v
```

### What the tests cover

| Area | What is verified |
|---|---|
| **Task** | Completion status, priority validation, schedulability checks |
| **Pet** | Empty task list on creation, task count after adding, profile output |
| **Owner** | No pets → empty task list, task aggregation across multiple pets |
| **Scheduler (core)** | Time budget respected, high priority wins when time is tight, reset works |
| **Sorting** | Tasks returned in HH:MM order, untimed tasks placed last |
| **Filtering** | Filter by pet name, filter by completion status, unknown pet returns empty |
| **Recurring tasks** | Next occurrence created on completion, correct due date (+1 day / +7 days) |
| **Conflict detection** | Same start_time flagged, different times pass, no-time tasks never conflict |

### Confidence level

⭐⭐⭐⭐ (4/5)

The core scheduling logic, recurring tasks, sorting, filtering, and conflict detection
are all well covered. The main gap is overlap detection — two tasks at 08:00 and 08:15
where the first runs 30 minutes would not be flagged. This is a known tradeoff
(documented in reflection.md) that would require time-range comparison logic to address.

