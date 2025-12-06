import random
from bakery import assert_equal
from drafter import *
from dataclasses import dataclass, field

# Website setup
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

# ---------------------
# Global State & ID generator
# ---------------------

GLOBAL_STATE = State()
_id_counter = 0

def generate_id():
    global _id_counter
    _id_counter += 1
    return f"id-{_id_counter}"

# ---------------------
# Routes
# ---------------------

@route
def index() -> Page:
    return Page(GLOBAL_STATE, [
        "Welcome to the pet care tracker!",
        "Please input information about one of your pets",
        "Name:", TextBox("name", ""),
        "Age (Numerical):", TextBox("age", ""),
        "Species:", TextBox("species", ""),
        "Tasks (Comma Separated):", TextBox("tasks", ""),
        Button("Submit Pet", "/makepet")
    ])

@route
def makepet(name: str = "", age: str = "", species: str = "", tasks: str = "") -> Page:
    task_list = [t.strip() for t in tasks.split(",") if t.strip()]
    pet = Pet(name, int(age), species, task_list, [False]*len(task_list), generate_id())
    GLOBAL_STATE.pet_list.append(pet)
    return petview()

@route
def petview() -> Page:
    if not GLOBAL_STATE.pet_list:
        return index()
    elements = ["View your pets' pages below:"]
    for pet in GLOBAL_STATE.pet_list:
        status = "✅ All tasks done!" if all(pet.task_done) else "❌ Tasks remaining"
        elements.append(f"{pet.name} - {status}")
        elements.append(Button(f"View Tasks for {pet.name}", f"/taskview/{pet.id}"))
    elements.append(Button("Add New Pet", "/new_pet"))
    return Page(GLOBAL_STATE, elements)

@route("/taskview/<pet_id>")
def taskview(pet_id: str) -> Page:
    pet = next((p for p in GLOBAL_STATE.pet_list if p.id == pet_id), None)
    if not pet:
        return Page(GLOBAL_STATE, ["Pet not found."])
    content = [
        f"Pet Name: {pet.name}",
        f"Pet Species: {pet.species}",
        f"Pet Age: {pet.age}",
        "Tasks:"
    ]
    for i, task in enumerate(pet.care_tasks):
        status = "✅" if pet.task_done[i] else "❌"
        content.append(f"{task} {status}")
        content.append(Button(f"Toggle Task {i}", f"/toggletask/{pet.id}/{i}"))
    content.append(Button("Edit Pet", f"/editpet/{pet.id}"))
    content.append(Button("Delete Pet", f"/deletepet/{pet.id}"))
    content.append(Button("Return to Main Page", "/petview"))
    return Page(GLOBAL_STATE, content)

@route("/deletepet/<pet_id>")
def deletepet(pet_id: str) -> Page:
    GLOBAL_STATE.pet_list = [p for p in GLOBAL_STATE.pet_list if p.id != pet_id]
    return petview()

@route("/editpet/<pet_id>")
def editpet(pet_id: str) -> Page:
    pet = next((p for p in GLOBAL_STATE.pet_list if p.id == pet_id), None)
    if not pet:
        return Page(GLOBAL_STATE, ["Pet not found."])
    return Page(GLOBAL_STATE, [
        "Edit Pet Information:",
        "Name:", TextBox("name", pet.name),
        "Age:", TextBox("age", str(pet.age)),
        "Species:", TextBox("species", pet.species),
        "Tasks (comma separated):", TextBox("tasks", ", ".join(pet.care_tasks)),
        Button("Save Changes", f"/savepet/{pet.id}"),
        Button("Cancel", f"/taskview/{pet.id}")
    ])

@route("/savepet/<pet_id>")
def savepet(pet_id: str, name: str = "", age: str = "", species: str = "", tasks: str = "") -> Page:
    pet = next((p for p in GLOBAL_STATE.pet_list if p.id == pet_id), None)
    if not pet:
        return Page(GLOBAL_STATE, ["Pet not found."])
    task_list = [t.strip() for t in tasks.split(",") if t.strip()]
    old_task_done = pet.task_done[:]
    pet.task_done = [old_task_done[i] if i < len(old_task_done) else False for i in range(len(task_list))]
    pet.name = name
    pet.age = int(age)
    pet.species = species
    pet.care_tasks = task_list
    return taskview(pet_id=pet.id)

@route("/toggletask/<pet_id>/<task_index>")
def toggletask(pet_id: str, task_index: str) -> Page:
    task_index = int(task_index)
    pet = next((p for p in GLOBAL_STATE.pet_list if p.id == pet_id), None)
    if not pet:
        return Page(GLOBAL_STATE, ["Pet not found."])
    pet.task_done[task_index] = not pet.task_done[task_index]
    return taskview(pet_id=pet.id)

@route
def new_pet() -> Page:
    return Page(GLOBAL_STATE, [
        "Please input information about your pet",
        "Name:", TextBox("name", ""),
        "Age (Numerical):", TextBox("age", ""),
        "Species:", TextBox("species", ""),
        "Tasks (Comma Separated):", TextBox("tasks", ""),
        Button("Submit Pet", "/makepet")
    ])

# ---------------------
# Start the server
# ---------------------

start_server(GLOBAL_STATE)
