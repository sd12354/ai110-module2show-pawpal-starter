import os

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, is_valid_time

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant. Add your pets, give them tasks, and get a daily schedule.")

# Streamlit reruns the whole script on every click, so the Owner object is kept
# in session_state. That way the pets and tasks stay around between reruns
# instead of being rebuilt empty each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
if "show_schedule" not in st.session_state:
    st.session_state.show_schedule = False
if "flash" not in st.session_state:
    # A one-time message to show after a rerun (e.g. "queued tomorrow's walk").
    st.session_state.flash = None

owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- Owner ---
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

# --- Add a pet ---
st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    new_pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if new_pet_name.strip() and owner.get_pet(new_pet_name.strip()) is None:
        owner.add_pet(Pet(new_pet_name.strip(), new_pet_species))
        st.success(f"Added {new_pet_name.strip()}.")
    else:
        st.warning("That pet name is empty or already taken.")

# --- Add a task ---
if owner.pets:
    st.subheader("Add a Task")
    pet_names = [pet.name for pet in owner.pets]
    chosen_pet = st.selectbox("Which pet?", pet_names)

    c1, c2 = st.columns(2)
    with c1:
        task_title = st.text_input("Task", value="Morning walk")
        task_time = st.text_input("Time (HH:MM, 24-hour)", value="08:00")
    with c2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        if not task_title.strip():
            st.error("Give the task a name.")
        elif not is_valid_time(task_time.strip()):
            st.error("Time must look like HH:MM in 24-hour format, e.g. 08:00 or 18:30.")
        else:
            pet = owner.get_pet(chosen_pet)
            pet.add_task(
                Task(task_title.strip(), task_time.strip(), int(duration), priority, frequency)
            )
            st.session_state.show_schedule = True
            st.success(f"Added '{task_title.strip()}' to {chosen_pet}.")
else:
    st.info("Add a pet first, then you can give it tasks.")

st.divider()

# --- Schedule ---
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    st.session_state.show_schedule = True

if st.session_state.flash:
    st.success(st.session_state.flash)
    st.session_state.flash = None

if st.session_state.show_schedule:
    if not owner.all_tasks():
        st.info("No tasks yet. Add some above.")
    else:
        # View controls: every option maps to a Scheduler method.
        f1, f2, f3 = st.columns(3)
        with f1:
            sort_mode = st.radio("Sort by", ["Time", "Priority"], horizontal=True)
        with f2:
            pet_filter = st.selectbox("Pet", ["All pets"] + [pet.name for pet in owner.pets])
        with f3:
            status_filter = st.selectbox("Status", ["To do", "Done", "All"])

        # Start from the sorted list, then narrow it down with the filters.
        if sort_mode == "Priority":
            tasks = scheduler.sort_by_priority()
        else:
            tasks = scheduler.sort_by_time()

        if pet_filter != "All pets":
            allowed = set(id(t) for t in scheduler.filter_by_pet(pet_filter))
            tasks = [t for t in tasks if id(t) in allowed]

        if status_filter == "To do":
            tasks = [t for t in tasks if not t.completed]
        elif status_filter == "Done":
            tasks = [t for t in tasks if t.completed]

        # Map each task back to its pet so the table can show who it is for.
        pet_of = {id(task): pet.name for pet in owner.pets for task in pet.tasks}

        if not tasks:
            st.info("Nothing matches those filters.")
        else:
            rows = []
            for task in tasks:
                rows.append(
                    {
                        "Pet": pet_of.get(id(task), "?"),
                        "Time": task.time,
                        "Task": task.description,
                        "Minutes": task.duration_minutes,
                        "Priority": task.priority,
                        "Repeats": task.frequency,
                        "Due": task.due_date.isoformat(),
                        "Done": "✅" if task.completed else "⬜",
                    }
                )
            st.table(rows)

        # Conflict warnings come straight from the Scheduler.
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(f"⚠️ {warning}. Consider moving one of them.")
        else:
            st.success("No scheduling conflicts found.")

        # Mark tasks complete. Recurring tasks get their next occurrence queued
        # automatically by Scheduler.mark_task_complete().
        todo = [t for t in tasks if not t.completed]
        if todo:
            st.markdown("**Mark a task as done**")
            for i, task in enumerate(todo):
                label = f"✔ {task.time} {task.description} ({pet_of.get(id(task), '?')})"
                if st.button(label, key=f"done_{i}_{id(task)}"):
                    scheduler.mark_task_complete(task)
                    if task.is_recurring():
                        nxt = task.next_occurrence()
                        st.session_state.flash = (
                            f"Marked '{task.description}' done. It repeats {task.frequency}, "
                            f"so it was re-queued for {nxt.due_date} at {nxt.time}."
                        )
                    else:
                        st.session_state.flash = f"Marked '{task.description}' done."
                    st.rerun()

st.divider()

# --- Persistence ---
st.subheader("Save / Load")
st.caption(f"Data is stored in `{DATA_FILE}` next to this app so it survives a restart.")
s1, s2 = st.columns(2)
with s1:
    if st.button("💾 Save to file"):
        owner.save_to_json(DATA_FILE)
        st.success(f"Saved {len(owner.pets)} pet(s) and {len(owner.all_tasks())} task(s).")
with s2:
    if st.button("📂 Load from file"):
        if os.path.exists(DATA_FILE):
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
            st.session_state.show_schedule = True
            st.session_state.flash = f"Loaded {DATA_FILE}."
            st.rerun()
        else:
            st.error(f"No {DATA_FILE} found yet. Save first.")
