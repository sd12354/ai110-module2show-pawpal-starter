"""PawPal+ logic layer.

This file holds the core classes for the PawPal+ pet care app. Both the
Streamlit UI in app.py and the demo script in main.py import from here, so
all of the real logic lives in this one place.
"""

from dataclasses import dataclass, field
from datetime import date


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

    def todays_schedule(self):
        """Return today's unfinished tasks, sorted by time."""
        today = date.today()
        todo = [
            task
            for task in self.owner.all_tasks()
            if not task.completed and task.due_date == today
        ]
        return sorted(todo, key=lambda task: task.time)
