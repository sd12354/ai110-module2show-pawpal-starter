"""Quick CLI demo for PawPal+.

Run it with: python main.py

It builds an owner with two pets, adds a few tasks, and prints today's
schedule. This is the "testing ground" that proves the logic in
pawpal_system.py works before it gets wired into the Streamlit app.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "cat")
    biscuit = Pet("Biscuit", "dog")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    mochi.add_task(Task("Morning feeding", "08:00", 10, "high", "daily"))
    biscuit.add_task(Task("Evening walk", "18:00", 30, "high", "daily"))
    mochi.add_task(Task("Give medication", "12:00", 5, "high", "weekly"))

    scheduler = Scheduler(owner)
    print("Today's Schedule")
    print("-" * 40)
    for task in scheduler.todays_schedule():
        print(
            f"{task.time}  {task.description} "
            f"({task.duration_minutes} min) [priority: {task.priority}]"
        )


if __name__ == "__main__":
    main()
