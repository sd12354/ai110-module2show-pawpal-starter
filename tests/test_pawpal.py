"""Tests for the PawPal+ logic layer."""

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
