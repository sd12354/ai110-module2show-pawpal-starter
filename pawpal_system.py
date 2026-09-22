"""PawPal+ logic layer.

This file holds the core classes for the PawPal+ pet care app. Both the
Streamlit UI in app.py and the demo script in main.py import from here, so
all of the real logic lives in this one place.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

# Lower number = more urgent. Used by Scheduler.sort_by_priority().
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single pet care task such as a walk, a feeding, or a medication."""

    description: str
    time: str  # 24-hour clock as "HH:MM"
    duration_minutes: int = 30
    priority: str = "medium"  # "low", "medium", or "high"
    frequency: str = "once"  # "once", "daily", or "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def is_recurring(self):
        """Return True if the task repeats daily or weekly."""
        return self.frequency in ("daily", "weekly")

    def next_occurrence(self):
        """Build the next copy of a recurring task on its next due date."""
        if self.frequency == "daily":
            next_date = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = self.due_date + timedelta(weeks=1)
        else:
            return None
        return Task(
            description=self.description,
            time=self.time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            completed=False,
            due_date=next_date,
        )


@dataclass
class Pet:
    """A pet that belongs to an owner and keeps its own list of tasks."""

    name: str
    species: str = "dog"
    tasks: list = field(default_factory=list)

    def add_task(self, task):
        """Add a task to this pet's list."""
        self.tasks.append(task)

    def task_count(self):
        """Return how many tasks this pet has."""
        return len(self.tasks)


class Owner:
    """A pet owner who can have several pets at once."""

    def __init__(self, name):
        self.name = name
        self.pets = []

    def add_pet(self, pet):
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name):
        """Find one of the owner's pets by name, or None if there isn't one."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def all_tasks(self):
        """Return every task across all of the owner's pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Scheduler:
    """The brain of PawPal+. It reads tasks from an owner and organizes them."""

    def __init__(self, owner):
        self.owner = owner

    def sort_by_time(self):
        """Return all of the owner's tasks ordered by their HH:MM start time."""
        return sorted(self.owner.all_tasks(), key=lambda task: task.time)

    def sort_by_priority(self):
        """Return all tasks ordered high -> medium -> low, then by time within a level."""
        return sorted(
            self.owner.all_tasks(),
            key=lambda task: (PRIORITY_RANK.get(task.priority, len(PRIORITY_RANK)), task.time),
        )

    def filter_by_status(self, completed):
        """Return only the tasks that match a completion status (True or False)."""
        return [task for task in self.owner.all_tasks() if task.completed == completed]

    def filter_by_pet(self, pet_name):
        """Return only the tasks that belong to one pet."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return []
        return list(pet.tasks)

    def todays_schedule(self):
        """Return today's unfinished tasks, sorted by time."""
        today = date.today()
        todo = [
            task
            for task in self.owner.all_tasks()
            if not task.completed and task.due_date == today
        ]
        return sorted(todo, key=lambda task: task.time)

    def mark_task_complete(self, task):
        """Mark a task done and, if it repeats, queue up the next occurrence."""
        task.mark_complete()
        if task.is_recurring():
            pet = self._find_pet_for_task(task)
            if pet is not None:
                pet.add_task(task.next_occurrence())

    def _find_pet_for_task(self, task):
        """Find which pet a given task belongs to."""
        for pet in self.owner.pets:
            if task in pet.tasks:
                return pet
        return None

    def detect_conflicts(self):
        """Return a warning string for any two unfinished tasks that share a day and a time.

        Completed tasks are skipped, and two tasks only clash if they fall on the
        same due_date. Without the date check, a daily task's next occurrence
        (tomorrow at 08:00) would be flagged against today's 08:00 task.
        """
        warnings = []
        tasks = [task for task in self.sort_by_time() if not task.completed]
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                same_day = tasks[i].due_date == tasks[j].due_date
                if same_day and tasks[i].time == tasks[j].time:
                    warnings.append(
                        f"Conflict at {tasks[i].time}: "
                        f"'{tasks[i].description}' and '{tasks[j].description}'"
                    )
        return warnings
