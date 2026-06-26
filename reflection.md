# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I went with four classes because that matched how I already think about the situation. A Task is one thing a pet needs, like a walk or a feeding, and it holds the description, the time, how long it takes, the priority, how often it repeats, and whether it is done. A Pet has a name and a species and keeps its own list of tasks. An Owner can have more than one pet, so it holds a list of pets and can hand back every task across all of them. The Scheduler does not hold any data of its own. It takes an owner and does the thinking part, like sorting the tasks and finding conflicts. I made Task and Pet dataclasses so I did not have to write a long init method by hand.

**b. Design changes**

My design did change once I started building. My first version of Task only had a time string like "08:00" and no real date. That was fine until I tried to make daily tasks repeat, because to move a task to the next day I needed an actual date to add a day to, and you cannot add a day to "08:00". So I added a due_date field that defaults to today and used timedelta to figure out the next one. The other change was where the scheduling logic lived. At first I started putting the sorting inside the Owner class, but it got cramped, so I pulled all of that out into the Scheduler. That kept the data classes simple and put all the algorithms in one spot.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler looks at the time of each task, whether it is finished, and which pet it belongs to. Each task also stores a priority and a duration. I decided time mattered the most because a daily plan is something you read from top to bottom during the day, so putting everything in order by time is what actually helps the owner. Priority is there too, but I used time as the main sort key since two tasks at 8am are both happening in the morning no matter what their priority is.

**b. Tradeoffs**

The biggest tradeoff is that my conflict detection only catches tasks that have the exact same time. It does not look at how long a task takes. So a 30 minute walk at 08:00 and a feeding at 08:15 would not get flagged even though they really do overlap. I think that is reasonable for this app because most pet tasks are short and an owner can usually shuffle a few minutes on their own. Checking exact times keeps the code short and easy to read, and I can always add duration overlap later if I need it.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI in a few different ways. First I had it help me brainstorm the UML diagram once I told it the four classes and what each one should hold. Then I asked it to turn that diagram into class skeletons so I had a starting point. The most useful prompts were the specific ones where I attached my file and asked a narrow question, like how to sort time strings in "HH:MM" order with a lambda, or how to use timedelta to get the next day. Vague prompts gave me long answers I did not need, but pointed questions about my own code gave me stuff I could actually use.

**b. Judgment and verification**

There was one spot where the AI gave me a fancier version of my conflict detection that used a dictionary to group tasks by time. It was shorter, but I had a harder time explaining how it worked, and this is my project to understand. I kept my own version with two loops because I can read it and explain exactly what it does, even if it is a little longer. To check my code in general I leaned on running main.py and the tests instead of just trusting the AI. If the schedule printed in the right order and the conflict showed up, I knew it worked.

---

## 4. Testing and Verification

**a. What you tested**

I tested five things: that mark_complete actually flips a task to done, that adding a task to a pet bumps its task count, that sort_by_time returns tasks in time order, that finishing a daily task creates a new copy for the next day, and that the scheduler flags two tasks at the same time. These were important because they are the core promises of the app. If sorting or conflict detection broke, the whole point of the scheduler would be gone.

**b. Confidence**

I am pretty confident, around a 4 out of 5. All five tests pass and they hit the parts I was most worried about. The thing keeping me from a 5 is the edge cases I have not covered yet. If I had more time I would test overlapping durations, a pet that has no tasks at all, a weird time string like "25:99", and what happens right at midnight when "today" rolls over.

---

## 5. Reflection

**a. What went well**

I am most happy with how the Scheduler turned out as its own class. Keeping all the algorithms in one place made the data classes really clean and made it easy to add features like filtering without touching Pet or Owner. Seeing the sorting and the conflict warning work together in the demo felt good.

**b. What you would improve**

If I did another round I would store the time as a real datetime instead of a string. That would let me handle duration overlaps and would make sorting more solid than comparing text. I would also make the Streamlit page let you mark a task complete with a button, so the recurring logic shows up in the UI and not just in the tests.

**c. Key takeaway**

The biggest thing I learned is that designing the structure first with UML made the actual coding way smoother, because I already knew what each class was responsible for before I wrote it. I also learned that being the lead architect means I have to read and judge what the AI gives me instead of just pasting it in. The AI is fast, but I am the one who has to understand the code and stand behind it.
