import traceback
from bakery import assert_equal
from drafter import *
from dataclasses import dataclass, field

# ---------------------
# Website setup
# ---------------------
set_website_title("Your Drafter Website")
set_site_information(
    "egrunw@udel.edu",
    """
A website that keeps track of your pets and what tasks have been done for them.
""",
    [],
    [],
    [],
)

# ---------------------
# Data Classes
# ---------------------
@dataclass
class Pet:
    name: str
    age: int
    species: str
    care_tasks: list[str]
    task_done: list[bool]
    id: str

@dataclass
class State:
    pet_list: list[Pet] = field(default_factory=list)
    _id_counter: int = 0  # For generating unique IDs

# ---------------------
# Helpers
# ---------------------
def generate_id(state: State) -> str:
    state._id_counter += 1
    return f"id-{state._id_counter}"

def safe_pad_task_done(pet: Pet) -> None:
    """Ensure pet.task_done length matches pet.care_tasks length."""
    if len(pet.task_done) < len(pet.care_tasks):
        pet.task_done.extend([False] * (len(pet.care_tasks) - len(pet.task_done)))
    elif len(pet.task_done) > len(pet.care_tasks):
        # Trim extras (shouldn't normally happen)
        pet.task_done = pet.task_done[:len(pet.care_tasks)]

def page_on_exception(state: State, exc: Exception) -> Page:
    """Return a page showing the error (and print traceback to console)."""
    print("----- Exception in route -----")
    traceback.print_exc()
    err_text = f"Error: {type(exc).__name__}: {exc}"
    # Small, safe sanitized message for the browser
    return Page(state, [
        "An internal error occurred.",
        err_text,
        Button("Return to Main Page", "/petview")
    ])

# ---------------------
# Routes (state-first signatures)
# ---------------------
@route
def index(state: State) -> Page:
    try:
        return Page(state, [
            "Welcome to the pet care tracker!",
            "Please input information about one of your pets",
            "Name:", TextBox("name", ""),
            "Age (Numerical):", TextBox("age", ""),
            "Species:", TextBox("species", ""),
            "Tasks (Comma Separated):", TextBox("tasks", ""),
            Button("Submit Pet", "/makepet")
        ])
    except Exception as e:
        return page_on_exception(state, e)

@route
def makepet(state: State, name: str = "", age: str = "", species: str = "", tasks: str = "") -> Page:
    try:
        # Validate and parse
        try:
            age_int = int(age)
        except Exception:
            return Page(state, ["Invalid age — please enter a number.", Button("Return", "/")])

        task_list = [t.strip() for t in tasks.split(",") if t.strip()]
        pet = Pet(
            name=name,
            age=age_int,
            species=species,
            care_tasks=task_list,
            task_done=[False] * len(task_list),
            id=generate_id(state),
        )
        safe_pad_task_done(pet)
        state.pet_list.append(pet)
        return petview(state)
    except Exception as e:
        return page_on_exception(state, e)

@route
def petview(state: State) -> Page:
    try:
        if not state.pet_list:
            return index(state)
        elements = ["View your pets' pages below:"]
        for pet in state.pet_list:
            safe_pad_task_done(pet)
            status = "✅ All tasks done!" if all(pet.task_done) and pet.care_tasks else "❌ Tasks remaining"
            elements.append(f"{pet.name} - {status}")
            elements.append(Button(f"View Tasks for {pet.name}", f"/taskview/{pet.id}"))
        elements.append(Button("Add New Pet", "/new_pet"))
        return Page(state, elements)
    except Exception as e:
        return page_on_exception(state, e)

@route("/taskview/<pet_id>")
def taskview(state: State, pet_id: str) -> Page:
    try:
        pet = next((p for p in state.pet_list if p.id == pet_id), None)
        if not pet:
            return Page(state, ["Pet not found.", Button("Return", "/petview")])
        safe_pad_task_done(pet)

        content = [
            f"Pet Name: {pet.name}",
            f"Pet Species: {pet.species}",
            f"Pet Age: {pet.age}",
            "Tasks:"
        ]
        for i, task in enumerate(pet.care_tasks):
            # double-check index safety
            status = "✅" if (i < len(pet.task_done) and pet.task_done[i]) else "❌"
            content.append(f"{task} {status}")
            content.append(Button(f"Toggle Task {i}", f"/toggletask/{pet.id}/{i}"))

        content.append(Button("Edit Pet", f"/editpet/{pet.id}"))
        content.append(Button("Delete Pet", f"/deletepet/{pet.id}"))
        content.append(Button("Return to Main Page", "/petview"))
        return Page(state, content)
    except Exception as e:
        return page_on_exception(state, e)

@route("/deletepet/<pet_id>")
def deletepet(state: State, pet_id: str) -> Page:
    try:
        state.pet_list = [p for p in state.pet_list if p.id != pet_id]
        return petview(state)
    except Exception as e:
        return page_on_exception(state, e)

@route("/editpet/<pet_id>")
def editpet(state: State, pet_id: str) -> Page:
    try:
        pet = next((p for p in state.pet_list if p.id == pet_id), None)
        if not pet:
            return Page(state, ["Pet not found.", Button("Return", "/petview")])
        safe_pad_task_done(pet)
        return Page(state, [
            "Edit Pet Information:",
            "Name:", TextBox("name", pet.name),
            "Age:", TextBox("age", str(pet.age)),
            "Species:", TextBox("species", pet.species),
            "Tasks (comma separated):", TextBox("tasks", ", ".join(pet.care_tasks)),
            Button("Save Changes", f"/savepet/{pet.id}"),
            Button("Cancel", f"/taskview/{pet.id}")
        ])
    except Exception as e:
        return page_on_exception(state, e)

@route("/savepet/<pet_id>")
def savepet(state: State, pet_id: str, name: str = "", age: str = "", species: str = "", tasks: str = "") -> Page:
    try:
        pet = next((p for p in state.pet_list if p.id == pet_id), None)
        if not pet:
            return Page(state, ["Pet not found.", Button("Return", "/petview")])
        try:
            age_int = int(age)
        except Exception:
            return Page(state, ["Invalid age — please enter a number.", Button("Return", f"/editpet/{pet.id}")])

        task_list = [t.strip() for t in tasks.split(",") if t.strip()]
        old_task_done = pet.task_done[:]
        pet.task_done = [old_task_done[i] if i < len(old_task_done) else False for i in range(len(task_list))]
        pet.name = name
        pet.age = age_int
        pet.species = species
        pet.care_tasks = task_list
        safe_pad_task_done(pet)
        return taskview(state, pet.id)
    except Exception as e:
        return page_on_exception(state, e)

@route("/toggletask/<pet_id>/<task_index>")
def toggletask(state: State, pet_id: str, task_index: str) -> Page:
    try:
        # validate and convert
        try:
            idx = int(task_index)
        except Exception:
            return Page(state, ["Invalid task index.", Button("Return", f"/taskview/{pet_id}")])
        pet = next((p for p in state.pet_list if p.id == pet_id), None)
        if not pet:
            return Page(state, ["Pet not found.", Button("Return", "/petview")])
        safe_pad_task_done(pet)
        if idx < 0 or idx >= len(pet.care_tasks):
            return Page(state, ["Task index out of range.", Button("Return", f"/taskview/{pet_id}")])
        pet.task_done[idx] = not pet.task_done[idx]
        return taskview(state, pet.id)
    except Exception as e:
        return page_on_exception(state, e)

@route
def new_pet(state: State) -> Page:
    try:
        return Page(state, [
            "Please input information about your pet",
            "Name:", TextBox("name", ""),
            "Age (Numerical):", TextBox("age", ""),
            "Species:", TextBox("species", ""),
            "Tasks (Comma Separated):", TextBox("tasks", ""),
            Button("Submit Pet", "/makepet")
        ])
    except Exception as e:
        return page_on_exception(state, e)

# ---------------------
# Start server
# ---------------------
start_server(State())
