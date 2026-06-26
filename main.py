"""Quick CLI demo for PawPal+.

Run it with: python main.py

It builds an owner with two pets, adds a few tasks on purpose out of order,
and then prints today's schedule plus any conflicts the scheduler finds. This
is the "testing ground" that proves the logic in pawpal_system.py works before
it gets wired into the Streamlit app.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(scheduler):
    """Print every task in time order in a way that is easy to read."""
    tasks = scheduler.sort_by_time()
    print("Today's Schedule")
    print("-" * 40)
    for task in tasks:
        status = "done" if task.completed else "todo"
        print(
            f"{task.time}  {task.description} "
            f"({task.duration_minutes} min) "
            f"[priority: {task.priority}] [{status}]"
        )


def main():
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "cat")
    biscuit = Pet("Biscuit", "dog")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # Added out of order on purpose so the scheduler has to sort them.
    biscuit.add_task(Task("Evening walk", "18:00", 30, "high", "daily"))
    mochi.add_task(Task("Morning feeding", "08:00", 10, "high", "daily"))
    biscuit.add_task(Task("Morning walk", "08:00", 30, "high", "daily"))
    mochi.add_task(Task("Give medication", "12:00", 5, "high", "weekly"))

    scheduler = Scheduler(owner)
    print_schedule(scheduler)

    print()
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("Conflict warnings:")
        for warning in conflicts:
            print(f"  - {warning}")
    else:
        print("No conflicts found.")


if __name__ == "__main__":
    main()
