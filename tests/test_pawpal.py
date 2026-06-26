"""Tests for the PawPal+ logic layer."""

from datetime import timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def test_mark_complete_changes_status():
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_count():
    pet = Pet("Mochi", "cat")
    assert pet.task_count() == 0
    pet.add_task(Task("Feeding", "08:00"))
    assert pet.task_count() == 1


def test_sort_by_time_is_chronological():
    owner = Owner("Jordan")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Evening walk", "18:00"))
    pet.add_task(Task("Morning walk", "08:00"))
    pet.add_task(Task("Lunch", "12:00"))

    scheduler = Scheduler(owner)
    times = [task.time for task in scheduler.sort_by_time()]
    assert times == ["08:00", "12:00", "18:00"]


def test_daily_task_creates_next_occurrence():
    owner = Owner("Jordan")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    daily = Task("Morning walk", "08:00", frequency="daily")
    pet.add_task(daily)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete(daily)

    # One finished task, plus a fresh copy queued for the next day.
    assert pet.task_count() == 2
    new_task = pet.tasks[-1]
    assert new_task.completed is False
    assert new_task.due_date == daily.due_date + timedelta(days=1)


def test_conflict_detection_flags_same_time():
    owner = Owner("Jordan")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", "08:00"))
    pet.add_task(Task("Feeding", "08:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
