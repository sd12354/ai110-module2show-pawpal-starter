"""Tests for the PawPal+ logic layer.

Run with: python -m pytest
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def make_owner_with_pets():
    """Shared setup: one owner, a cat and a dog, no tasks yet."""
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "cat"))
    owner.add_pet(Pet("Biscuit", "dog"))
    return owner


# ---------- Task and Pet basics ----------


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


def test_owner_all_tasks_spans_every_pet():
    owner = make_owner_with_pets()
    owner.get_pet("Mochi").add_task(Task("Feeding", "08:00"))
    owner.get_pet("Biscuit").add_task(Task("Walk", "09:00"))
    owner.get_pet("Biscuit").add_task(Task("Brush", "10:00"))
    assert len(owner.all_tasks()) == 3


def test_get_pet_returns_none_for_unknown_name():
    owner = make_owner_with_pets()
    assert owner.get_pet("Nobody") is None


# ---------- Sorting ----------


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


def test_sort_by_time_merges_tasks_across_pets():
    owner = make_owner_with_pets()
    owner.get_pet("Biscuit").add_task(Task("Evening walk", "18:00"))
    owner.get_pet("Mochi").add_task(Task("Morning feeding", "08:00"))
    owner.get_pet("Biscuit").add_task(Task("Morning walk", "09:00"))

    names = [task.description for task in Scheduler(owner).sort_by_time()]
    assert names == ["Morning feeding", "Morning walk", "Evening walk"]


def test_sort_by_priority_puts_high_first_then_time():
    owner = make_owner_with_pets()
    pet = owner.get_pet("Biscuit")
    pet.add_task(Task("Brush coat", "07:00", priority="low"))
    pet.add_task(Task("Evening walk", "18:00", priority="high"))
    pet.add_task(Task("Play", "10:00", priority="medium"))
    pet.add_task(Task("Morning walk", "08:00", priority="high"))

    names = [task.description for task in Scheduler(owner).sort_by_priority()]
    assert names == ["Morning walk", "Evening walk", "Play", "Brush coat"]


def test_scheduler_handles_owner_with_no_tasks():
    owner = make_owner_with_pets()  # pets exist, but nothing scheduled
    scheduler = Scheduler(owner)
    assert scheduler.sort_by_time() == []
    assert scheduler.sort_by_priority() == []
    assert scheduler.todays_schedule() == []
    assert scheduler.detect_conflicts() == []


# ---------- Filtering ----------


def test_filter_by_status_splits_done_and_todo():
    owner = make_owner_with_pets()
    pet = owner.get_pet("Mochi")
    done = Task("Feeding", "08:00")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Play", "10:00"))

    scheduler = Scheduler(owner)
    assert [t.description for t in scheduler.filter_by_status(completed=True)] == ["Feeding"]
    assert [t.description for t in scheduler.filter_by_status(completed=False)] == ["Play"]


def test_filter_by_pet_returns_only_that_pets_tasks():
    owner = make_owner_with_pets()
    owner.get_pet("Mochi").add_task(Task("Feeding", "08:00"))
    owner.get_pet("Biscuit").add_task(Task("Walk", "09:00"))

    scheduler = Scheduler(owner)
    assert [t.description for t in scheduler.filter_by_pet("Biscuit")] == ["Walk"]
    assert scheduler.filter_by_pet("Nobody") == []


def test_todays_schedule_excludes_done_and_future_tasks():
    owner = make_owner_with_pets()
    pet = owner.get_pet("Biscuit")
    done = Task("Morning walk", "08:00")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Evening walk", "18:00"))
    pet.add_task(Task("Vet visit", "09:00", due_date=date.today() + timedelta(days=3)))

    names = [t.description for t in Scheduler(owner).todays_schedule()]
    assert names == ["Evening walk"]


# ---------- Recurring tasks ----------


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


def test_weekly_task_moves_seven_days_ahead():
    owner = make_owner_with_pets()
    pet = owner.get_pet("Mochi")
    weekly = Task("Give medication", "12:00", frequency="weekly")
    pet.add_task(weekly)

    Scheduler(owner).mark_task_complete(weekly)

    new_task = pet.tasks[-1]
    assert new_task.due_date == weekly.due_date + timedelta(weeks=1)
    assert new_task.time == "12:00"
    assert new_task.description == "Give medication"


def test_one_time_task_does_not_repeat():
    owner = make_owner_with_pets()
    pet = owner.get_pet("Biscuit")
    once = Task("Vet visit", "09:00", frequency="once")
    pet.add_task(once)

    Scheduler(owner).mark_task_complete(once)

    assert once.completed is True
    assert pet.task_count() == 1  # nothing new was queued
    assert once.next_occurrence() is None


# ---------- Conflict detection ----------


def test_conflict_detection_flags_same_time():
    owner = Owner("Jordan")
    pet = Pet("Biscuit", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", "08:00"))
    pet.add_task(Task("Feeding", "08:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1


def test_conflict_detection_works_across_pets():
    owner = make_owner_with_pets()
    owner.get_pet("Mochi").add_task(Task("Feeding", "08:00"))
    owner.get_pet("Biscuit").add_task(Task("Walk", "08:00"))

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "Feeding" in conflicts[0] and "Walk" in conflicts[0]


def test_no_conflict_when_times_differ():
    owner = make_owner_with_pets()
    pet = owner.get_pet("Biscuit")
    pet.add_task(Task("Walk", "08:00"))
    pet.add_task(Task("Feeding", "08:30"))

    assert Scheduler(owner).detect_conflicts() == []


def test_completed_task_does_not_cause_conflict():
    owner = make_owner_with_pets()
    pet = owner.get_pet("Biscuit")
    walk = Task("Walk", "08:00", frequency="daily")
    pet.add_task(walk)
    pet.add_task(Task("Feeding", "08:00"))

    scheduler = Scheduler(owner)
    assert len(scheduler.detect_conflicts()) == 1

    # Finishing the walk queues tomorrow's walk at 08:00, which must NOT be
    # flagged against today's feeding, and the finished walk must be ignored.
    scheduler.mark_task_complete(walk)
    assert scheduler.detect_conflicts() == []


# ---------- Persistence ----------


def test_save_and_load_json_round_trip(tmp_path):
    owner = make_owner_with_pets()
    owner.get_pet("Mochi").add_task(Task("Feeding", "08:00", 10, "high", "daily"))
    done = Task("Walk", "18:00", 30, "medium", "once")
    done.mark_complete()
    owner.get_pet("Biscuit").add_task(done)

    path = tmp_path / "data.json"
    owner.save_to_json(path)
    loaded = Owner.load_from_json(path)

    assert loaded.name == "Jordan"
    assert [pet.name for pet in loaded.pets] == ["Mochi", "Biscuit"]
    assert loaded.get_pet("Mochi").tasks[0] == owner.get_pet("Mochi").tasks[0]
    assert loaded.get_pet("Biscuit").tasks[0].completed is True
    assert loaded.to_dict() == owner.to_dict()
