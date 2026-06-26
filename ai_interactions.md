# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

After I had my UML diagram and class skeletons, I asked the agent to flesh out the whole logic layer in `pawpal_system.py`, build a demo in `main.py`, write tests, and then wire the classes into the Streamlit app. The goal was to go from empty stubs to a working scheduler that could sort tasks and catch conflicts.

**What did the agent do?**

It worked across a few files in a row. It filled in the four classes (making Task and Pet dataclasses), added the sorting, filtering, conflict detection, and recurring task methods to the Scheduler, wrote `main.py` to print a schedule, created `tests/test_pawpal.py`, and edited `app.py` so it imports the classes and keeps the Owner in `st.session_state`. After each big change it ran `python main.py` and `python -m pytest` to check that nothing broke.

**What did you have to verify or fix manually?**

The recurring task logic was the main thing I had to check. The first idea only stored a time string, so there was no way to move a task to the next day. I had it add a `due_date` field and use `timedelta` instead. I also went through the conflict detection myself to make sure I could explain it, since I would rather hand in code I understand than a clever version I cannot. I trusted the test output, but I still read every method before keeping it.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude (chat) | Claude (chat) |
| **Prompt** | "Write a function to find scheduling conflicts." | "In my Scheduler class, write a method that returns a warning string when two tasks share the exact same HH:MM time. Keep it simple with plain loops." |
| **Response summary** | A long function that parsed times into datetime objects and checked for overlapping ranges using durations. | A short `detect_conflicts` method with two nested loops that compares times and builds a list of warning strings. |
| **What was useful** | It showed me how overlap checking could work if I wanted durations later. | It matched my classes and was easy to read and explain. |
| **Problems noticed** | It was more than I asked for and harder to follow, and it assumed a time format I was not using yet. | It only catches exact time matches, not overlaps. |
| **Decision** | Saved the idea for later, did not use it now. | Used it. |

**Which approach did you use in your final implementation and why?**

I went with Option B. The vague prompt in Option A gave me a fancier answer with overlap math that I did not need yet and could not explain as easily. The specific prompt in Option B gave me a method that fit the design I already had, so I could read it, test it, and stand behind it. It taught me that telling the AI exactly what I want, in terms of my own code, gets me a better answer than a broad question.
