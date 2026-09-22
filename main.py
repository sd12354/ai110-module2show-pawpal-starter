"""Quick CLI demo for PawPal+.

Run it with: python main.py

It builds an owner with two pets, adds a few tasks on purpose out of order,
and then walks through everything the Scheduler can do: sort by time, sort by
priority, filter by pet and by status, flag conflicts, and roll a daily task
forward when it is marked complete. This is the "testing ground" that proves
the logic in pawpal_system.py works before it gets wired into the Streamlit app.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def format_task(task):
    """Return one task as a single readable line."""
    status = "done" if task.completed else "todo"
    return (
        f"{task.time}  {task.description:<18} "
        f"({task.duration_minutes:>2} min) "
        f"[priority: {task.priority:<6}] [{task.frequency:<6}] [{status}]"
    )


def print_section(title, tasks):
    """Print a titled block of tasks, or a friendly note if there are none."""
    print(title)
    print("-" * 72)
    if not tasks:
        print("  (no tasks)")
    for task in tasks:
        print(f"  {format_task(task)}")
    print()


def print_conflicts(scheduler):
    """Print the scheduler's conflict warnings, or say that there are none."""
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("Conflict warnings:")
        for warning in conflicts:
            print(f"  - {warning}")
    else:
        print("No conflicts found.")
    print()


def main():
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "cat")
    biscuit = Pet("Biscuit", "dog")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # Added out of order on purpose so the scheduler has to sort them.
    biscuit.add_task(Task("Evening walk", "18:00", 30, "medium", "daily"))
    mochi.add_task(Task("Morning feeding", "08:00", 10, "high", "daily"))
    biscuit.add_task(Task("Morning walk", "08:00", 30, "high", "daily"))
    mochi.add_task(Task("Give medication", "12:00", 5, "high", "weekly"))
    biscuit.add_task(Task("Brush coat", "15:00", 15, "low", "weekly"))

    scheduler = Scheduler(owner)

    # 1. Sorting
    print_section("Today's Schedule (sorted by time)", scheduler.sort_by_time())
    print_section("Same tasks, sorted by priority then time", scheduler.sort_by_priority())

    # 2. Conflict detection: two tasks share the 08:00 slot.
    print_conflicts(scheduler)

    # 3. Filtering
    print_section("Filter: only Mochi's tasks", scheduler.filter_by_pet("Mochi"))

    # 4. Recurring tasks: finishing a daily task queues the next one.
    morning_walk = biscuit.tasks[1]
    scheduler.mark_task_complete(morning_walk)
    next_walk = biscuit.tasks[-1]
    print(
        f"Marked '{morning_walk.description}' complete. It repeats {morning_walk.frequency}, "
        f"so a new copy was queued for {next_walk.due_date} at {next_walk.time}."
    )
    print()
    print_section("Filter: completed tasks", scheduler.filter_by_status(completed=True))
    print_section("Filter: still to do today", scheduler.todays_schedule())

    # 5. The finished walk no longer counts, so the 08:00 conflict clears.
    print_conflicts(scheduler)


if __name__ == "__main__":
    main()
