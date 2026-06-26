import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant. Add your pets, give them tasks, and get a daily schedule.")

# Streamlit reruns the whole script on every click, so the Owner object is kept
# in session_state. That way the pets and tasks stay around between reruns
# instead of being rebuilt empty each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner = st.session_state.owner

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
    if new_pet_name and owner.get_pet(new_pet_name) is None:
        owner.add_pet(Pet(new_pet_name, new_pet_species))
        st.success(f"Added {new_pet_name}.")
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
        task_time = st.text_input("Time (HH:MM)", value="08:00")
    with c2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        pet = owner.get_pet(chosen_pet)
        pet.add_task(
            Task(task_title, task_time, int(duration), priority, frequency)
        )
        st.success(f"Added '{task_title}' to {chosen_pet}.")
else:
    st.info("Add a pet first, then you can give it tasks.")

st.divider()

# --- Schedule ---
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    if not sorted_tasks:
        st.info("No tasks yet. Add some above.")
    else:
        rows = []
        for task in sorted_tasks:
            rows.append(
                {
                    "Time": task.time,
                    "Task": task.description,
                    "Minutes": task.duration_minutes,
                    "Priority": task.priority,
                    "Frequency": task.frequency,
                    "Done": "yes" if task.completed else "no",
                }
            )
        st.table(rows)

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No scheduling conflicts found.")
