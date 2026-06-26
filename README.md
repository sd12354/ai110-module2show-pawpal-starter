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

## 🖥️ Sample Output

Here is the output from running `python main.py`. It builds an owner with two pets, adds four tasks on purpose out of order, sorts them by time, and then checks for any tasks that land at the same time.

```
Today's Schedule
----------------------------------------
08:00  Morning feeding (10 min) [priority: high] [todo]
08:00  Morning walk (30 min) [priority: high] [todo]
12:00  Give medication (5 min) [priority: high] [todo]
18:00  Evening walk (30 min) [priority: high] [todo]

Conflict warnings:
  - Conflict at 08:00: 'Morning feeding' and 'Morning walk'
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

The suite covers the core behaviors: marking a task complete, adding a task to a pet, sorting tasks by time, the daily recurring logic, and conflict detection.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/sameerdhanda/ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 5 items

tests/test_pawpal.py .....                                               [100%]

============================== 5 passed in 0.01s ===============================
```

**Confidence Level:** 4 out of 5 stars. All five tests pass and they cover the behaviors I care about most. I dropped one star because I have not tested overlapping durations or bad time strings yet.

## 📐 Smarter Scheduling

These are the algorithms the `Scheduler` class adds on top of the basic data classes.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts every task by its "HH:MM" time using `sorted()` with a `lambda` key. |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Pull only the done/not done tasks, or only the tasks for one pet. |
| Conflict handling | `Scheduler.detect_conflicts()` | Compares tasks two at a time and returns a warning string when two share the same time. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | When a daily or weekly task is marked done, a new copy is queued for the next day or week using `timedelta`. |

## 📸 Demo Walkthrough

You can run the app with `streamlit run app.py`. Here is how a user moves through it:

1. Type the owner's name at the top of the page.
2. Add a pet by typing a name, picking a species, and clicking **Add pet**. You can add as many pets as you want.
3. Pick a pet, then fill in a task (what it is, the time in HH:MM, how long it takes, the priority, and how often it repeats) and click **Add task**.
4. Click **Generate schedule**. The app shows every task in time order in a table.
5. If two tasks land at the same time, a yellow warning shows up under the table telling you which two tasks clash. If nothing clashes, you get a green "no conflicts" message instead.

A quick example workflow: add a dog named Biscuit, give it a "Morning walk" at 08:00 and an "Evening walk" at 18:00, add a cat named Mochi with a "Morning feeding" at 08:00, then generate the schedule. The table comes back sorted by time, and because the walk and the feeding are both at 08:00, the app flags the conflict.

The same logic runs in the terminal through `main.py`. Here is the sample CLI output:

```
Today's Schedule
----------------------------------------
08:00  Morning feeding (10 min) [priority: high] [todo]
08:00  Morning walk (30 min) [priority: high] [todo]
12:00  Give medication (5 min) [priority: high] [todo]
18:00  Evening walk (30 min) [priority: high] [todo]

Conflict warnings:
  - Conflict at 08:00: 'Morning feeding' and 'Morning walk'
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
