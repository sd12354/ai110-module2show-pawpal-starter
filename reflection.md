# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Before drawing anything I wrote down the three things a user has to be able to do: (1) add a pet with a name and species, (2) schedule a task for that pet with a time, duration, priority, and how often it repeats, and (3) look at today's schedule in time order and get warned if two things collide. Everything in the design exists to support one of those three actions.

I went with four classes because that matched how I already think about the situation. A Task is one thing a pet needs, like a walk or a feeding, and it holds the description, the time, how long it takes, the priority, how often it repeats, and whether it is done. A Pet has a name and a species and keeps its own list of tasks. An Owner can have more than one pet, so it holds a list of pets and can hand back every task across all of them. The Scheduler does not hold any data of its own. It takes an owner and does the thinking part, like sorting the tasks and finding conflicts. I made Task and Pet dataclasses so I did not have to write a long init method by hand.

**b. Design changes**

My design did change once I started building. My first version of Task only had a time string like "08:00" and no real date. That was fine until I tried to make daily tasks repeat, because to move a task to the next day I needed an actual date to add a day to, and you cannot add a day to "08:00". So I added a due_date field that defaults to today and used timedelta to figure out the next one. The other change was where the scheduling logic lived. At first I started putting the sorting inside the Owner class, but it got cramped, so I pulled all of that out into the Scheduler. That kept the data classes simple and put all the algorithms in one spot.

When I came back to the project before submitting, the design grew a little more. I added `sort_by_priority()` to the Scheduler so priority actually does something, gave every class a `to_dict()` / `from_dict()` pair plus `save_to_json()` / `load_from_json()` on Owner so the data can survive a restart, and added a small `is_valid_time()` helper so the UI can reject a time like "25:99" before it ever becomes a Task. I kept the original draft in `diagrams/uml.mmd` and put the final version in `diagrams/uml_final.mmd`, so the two files show exactly what changed between the plan and the code.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler looks at the time of each task, whether it is finished, and which pet it belongs to. Each task also stores a priority and a duration. I decided time mattered the most because a daily plan is something you read from top to bottom during the day, so putting everything in order by time is what actually helps the owner. Priority is there too, but I used time as the main sort key since two tasks at 8am are both happening in the morning no matter what their priority is. Priority now gets its own view instead of being ignored: `sort_by_priority()` sorts by priority first and time second, and the app has a toggle between the two, so the owner can choose "what is next" or "what matters most."

**b. Tradeoffs**

The biggest tradeoff is that my conflict detection only catches tasks that have the exact same time. It does not look at how long a task takes. So a 30 minute walk at 08:00 and a feeding at 08:15 would not get flagged even though they really do overlap. I think that is reasonable for this app because most pet tasks are short and an owner can usually shuffle a few minutes on their own. Checking exact times keeps the code short and easy to read, and I can always add duration overlap later if I need it.

The exact-match rule also needed one refinement that I only found by extending the CLI demo. Once the demo marked a daily walk complete, the scheduler queued tomorrow's walk at 08:00 and then flagged it as a conflict with today's 08:00 feeding, and it kept flagging the walk that was already done. So `detect_conflicts()` now skips completed tasks and only compares tasks that share the same `due_date`. That is still a tradeoff: it means a conflict is "same day, same minute," nothing fancier, but it is the version I can explain in one sentence.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI in a few different ways. First I had it help me brainstorm the UML diagram once I told it the four classes and what each one should hold. Then I asked it to turn that diagram into class skeletons so I had a starting point. The most useful prompts were the specific ones where I attached my file and asked a narrow question, like how to sort time strings in "HH:MM" order with a lambda, or how to use timedelta to get the next day. Vague prompts gave me long answers I did not need, but pointed questions about my own code gave me stuff I could actually use.

The features that helped most were attaching files for context and letting the assistant edit across more than one file at a time. Attaching `pawpal_system.py` meant its answers used my real class and method names instead of made-up ones, and for the recurring-task change it needed to touch both `Task` and `Scheduler` at once, which would have been annoying to do by pasting snippets back and forth. Keeping the phases in separate chat sessions (design, core implementation, algorithms, testing, and then the pre-submission cleanup) also helped more than I expected. Each conversation stayed about one problem, the assistant was not dragging around stale context from an earlier phase, and it was easier for me to look back and remember why a decision was made. For the final pass I used Claude in agent mode and gave it the project instructions and my repo, and had it audit what was missing before changing anything.

**b. Judgment and verification**

There was one spot where the AI gave me a fancier version of my conflict detection that used a dictionary to group tasks by time. It was shorter, but I had a harder time explaining how it worked, and this is my project to understand. I kept my own version with two loops because I can read it and explain exactly what it does, even if it is a little longer. To check my code in general I leaned on running main.py and the tests instead of just trusting the AI. If the schedule printed in the right order and the conflict showed up, I knew it worked.

That habit paid off in the final pass. When the agent extended `main.py` to show recurrence, the very first run printed three conflict warnings instead of one, including a walk conflicting with its own next-day copy. The agent's output looked confident, but the numbers were wrong, and reading the output line by line is what caught it. The fix (skip completed tasks and require the same due date) went into `detect_conflicts()` along with a regression test, `test_completed_task_does_not_cause_conflict`, so it cannot quietly come back.

---

## 4. Testing and Verification

**a. What you tested**

I started with five tests for the core promises of the app: that mark_complete actually flips a task to done, that adding a task to a pet bumps its task count, that sort_by_time returns tasks in time order, that finishing a daily task creates a new copy for the next day, and that the scheduler flags two tasks at the same time. If sorting or conflict detection broke, the whole point of the scheduler would be gone.

The suite is now 20 tests. The additions are the edge cases I listed as "next time" in the first version: a pet with no tasks, tasks merged across two pets, priority-then-time ordering, filtering by status and by a pet that does not exist, today's schedule skipping done and future tasks, weekly recurrence landing seven days out, a one-time task not repeating, conflicts across pets, no conflict when times differ, no false conflict from a completed task or its re-queued copy, a save-and-load round trip through JSON, and the `is_valid_time()` helper rejecting things like "8:00" and "24:00."

**b. Confidence**

I am at a solid 4 out of 5. All 20 tests pass, and several of them exist specifically because something went wrong first (the false-conflict bug) or because I had written it down as a worry (empty pets, bad time strings). The thing keeping me from a 5 is that conflict detection still only checks exact time matches, so a 30-minute walk at 08:00 and a feeding at 08:15 pass silently. If I had more time I would test overlapping durations, what happens right at midnight when "today" rolls over and a re-queued task's date is compared against a new "today," and what `sort_by_priority()` should do with a priority string that is not low/medium/high (right now it just sorts last).

---

## 5. Reflection

**a. What went well**

I am most happy with how the Scheduler turned out as its own class. Keeping all the algorithms in one place made the data classes really clean and made it easy to add features like filtering without touching Pet or Owner. Seeing the sorting and the conflict warning work together in the demo felt good.

**b. What you would improve**

If I did another round I would store the time as a real datetime instead of a string. That would let me handle duration overlaps and would make sorting more solid than comparing text. In my first version I also wanted a button in the Streamlit page to mark a task complete so the recurring logic would show up in the UI and not just in the tests, and that is done now: every unfinished task has a ✔ button that calls `Scheduler.mark_task_complete()` and the app tells you when the next occurrence was queued. The next things on the list would be editing or deleting a task after it is created, and a "next free slot" suggestion that uses the durations I am already storing.

**c. Key takeaway**

The biggest thing I learned is that designing the structure first with UML made the actual coding way smoother, because I already knew what each class was responsible for before I wrote it. I also learned that being the lead architect means I have to read and judge what the AI gives me instead of just pasting it in. The AI is fast, but I am the one who has to understand the code and stand behind it.
