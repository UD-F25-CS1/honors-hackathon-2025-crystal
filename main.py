
from dataclasses import dataclass, field
from drafter import *


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


# -------------------- DATA MODELS --------------------
@dataclass
class Pet:
    name: str
    age: int
    species: str
    care_tasks: list[str]
    task_done: list[bool]

@dataclass
class State:
    pet_list: list[Pet] = field(default_factory=list)

# -------------------- INDEX / ADD PET --------------------
@route
def index(state: State) -> Page:
    return Page(state, [
        "Welcome to the pet care tracker!",
        "Please input information about one of your pets",
        "Name:", TextBox("name", ""),
        "Age (Numerical):", TextBox("age", ""),
        "Species:", TextBox("species", ""),
        "Tasks (Comma Separated):", TextBox("tasks", ""),
        Button("Submit Pet", "/makepet")
    ])

@route
def makepet(state: State, name: str, age: str, species: str, tasks: str) -> Page:
    task_list = [t.strip() for t in tasks.split(",") if t.strip()]
    pet = Pet(name, int(age), species, task_list, [False] * len(task_list))
    state.pet_list.append(pet)
    return petview(state)

# -------------------- MAIN PET LIST --------------------
@route
def petview(state: State) -> Page:
    if not state.pet_list:
        return index(state)

    elements = ["View your pets' pages below:"]

    for pet in state.pet_list:
        status = "✅ All tasks done!" if all(pet.task_done) else "❌ Tasks remaining"
        elements.append(f"{pet.name} - {status}")
        elements.append(Button(f"View Tasks for {pet.name}", f"/taskview/{pet.name}"))

    elements.append(Button("Add New Pet", "/new_pet"))
    return Page(state, elements)

# -------------------- TASK VIEW --------------------
@route("/taskview/<pet_name>")
def taskview(state: State, pet_name: str) -> Page:
    pet = next((p for p in state.pet_list if p.name == pet_name), None)
    if not pet:
        return Page(state, ["Pet not found."])

    content = [
        f"Pet Name: {pet.name}",
        f"Pet Species: {pet.species}",
        f"Pet Age: {pet.age}",
        "Tasks:"
    ]

    for i, task in enumerate(pet.care_tasks):
        status = "✅" if pet.task_done[i] else "❌"
        content.append(f"{task} {status}")
        content.append(Button(f"Toggle Task {i}", f"/toggletask/{pet.name}/{i}"))

    content.append(Button("Edit Pet", f"/editpet/{pet.name}"))
    content.append(Button("Delete Pet", f"/deletepet/{pet.name}"))
    content.append(Button("Return to Main Page", "/petview"))
    return Page(state, content)

# -------------------- DELETE PET --------------------
@route("/deletepet/<pet_name>")
def deletepet(state: State, pet_name: str) -> Page:
    state.pet_list = [p for p in state.pet_list if p.name != pet_name]
    return petview(state)

# -------------------- EDIT PET --------------------
@route("/editpet/<pet_name>")
def editpet(state: State, pet_name: str) -> Page:
    pet = next((p for p in state.pet_list if p.name == pet_name), None)
    if not pet:
        return Page(state, ["Pet not found."])

    return Page(state, [
        "Edit Pet Information:",
        "Name:", TextBox("name", pet.name),
        "Age:", TextBox("age", str(pet.age)),
        "Species:", TextBox("species", pet.species),
        "Tasks (comma separated):", TextBox("tasks", ", ".join(pet.care_tasks)),
        Button("Save Changes", f"/savepet/{pet.name}"),
        Button("Cancel", f"/taskview/{pet.name}")
    ])

# -------------------- SAVE PET CHANGES --------------------
@route("/savepet/<pet_name>")
def savepet(state: State, pet_name: str, name: str, age: str, species: str, tasks: str) -> Page:
    pet = next((p for p in state.pet_list if p.name == pet_name), None)
    if not pet:
        return Page(state, ["Pet not found."])

    task_list = [t.strip() for t in tasks.split(",") if t.strip()]

    # Preserve existing completed tasks where possible
    old_task_done = pet.task_done[:]
    pet.task_done = [
        old_task_done[i] if i < len(old_task_done) else False
        for i in range(len(task_list))
    ]

    # Update pet attributes
    pet.name = name
    pet.age = int(age)
    pet.species = species
    pet.care_tasks = task_list

    return taskview(state, pet.name)

# -------------------- TOGGLE TASK --------------------
@route("/toggletask/<pet_name>/<task_index>")
def toggletask(state: State, pet_name: str, task_index: str) -> Page:
    task_index = int(task_index)
    pet = next((p for p in state.pet_list if p.name == pet_name), None)
    if not pet:
        return Page(state, ["Pet not found."])

    pet.task_done[task_index] = not pet.task_done[task_index]
    return taskview(state, pet_name)

# -------------------- NEW PET PAGE --------------------
@route
def new_pet(state) -> Page:
    return Page(state, [
        "Please input information about your pet",
        "Name:", TextBox("name", ""),
        "Age (Numerical):", TextBox("age", ""),
        "Species:", TextBox("species", ""),
        "Tasks (Comma Separated):", TextBox("tasks", ""),
        Button("Submit Pet", "/makepet")
    ])

# -------------------- START SERVER --------------------
start_server(State())
