from bakery import assert_equal
from drafter import *
from dataclasses import dataclass
from uuid import uuid4
import importlib

uuid4 = importlib.import_module("uuid").uuid4


# hide_debug_information()
# set_website_framed(False)
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
    pet = Pet(name, int(age), species, task_list, [False]*len(task_list), str(uuid4()))
    state.pet_list.append(pet)
    return petview(state)


@route
def petview(state: State) -> Page:
    if not state.pet_list:
        return index(state)
    elements = ["View your pets' pages below:"]

    for pet in state.pet_list:
        status = "✅ All tasks done!" if all(pet.task_done) else "❌ Tasks remaining"
        elements.append(f"{pet.name} - {status}")
        elements.append(Button(f"View Tasks for {pet.name}", f"/taskview/{pet.id}"))
        
    elements.append(Button("Add New Pet", "/new_pet"))

    return Page(state, elements)

assert_equal(
 makepet(State(pet_list=[]), 'Alice', '3', 'Dog', 'Pet, feed'),
 Page(state=State(pet_list=[Pet(name='Alice',
                               age=3,
                               species='Dog',
                               care_tasks=['Pet', 'feed'],
                               task_done=[False, False],
                               id='f9271983-31b3-4a67-b4d1-b35f641a59b5')]),
     content=["View your pets' pages below:",
              'Alice - ❌ Tasks remaining',
              Button(text='View Tasks for Alice', url='/taskview/f9271983-31b3-4a67-b4d1-b35f641a59b5'),
              Button(text='Add New Pet', url='/new_pet')]))


@route("/taskview/<pet_id>")
def taskview(state: State, pet_id: str) -> Page:
    pet = next((p for p in state.pet_list if p.id == pet_id), None)
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
        # Button to toggle task completion
        content.append(Button(f"Toggle Task {i}", f"/toggletask/{pet.id}/{i}"))

    content.append(Button("Edit Pet", f"/editpet/{pet.id}"))
    content.append(Button("Delete Pet", f"/deletepet/{pet.id}"))
    content.append(Button("Return to Main Page", "/petview"))
    return Page(state, content)


@route("/deletepet/<pet_id>")
def deletepet(state: State, pet_id: str) -> Page:
    state.pet_list = [p for p in state.pet_list if p.id != pet_id]
    return petview(state)

@route("/editpet/<pet_id>")
def editpet(state: State, pet_id: str) -> Page:
    pet = next((p for p in state.pet_list if p.id == pet_id), None)
    if not pet:
        return Page(state, ["Pet not found."])

    return Page(state, [
        "Edit Pet Information:",
        "Name:", TextBox("name", pet.name),
        "Age:", TextBox("age", str(pet.age)),
        "Species:", TextBox("species", pet.species),
        "Tasks (comma separated):", TextBox("tasks", ", ".join(pet.care_tasks)),
        Button("Save Changes", f"/savepet/{pet.id}"),
        Button("Cancel", f"/taskview/{pet.id}")
    ])

@route("/savepet/<pet_id>")
def savepet(state: State, pet_id: str, name: str, age: str, species: str, tasks: str) -> Page:
    pet = next((p for p in state.pet_list if p.id == pet_id), None)
    if not pet:
        return Page(state, ["Pet not found."])

    task_list = [t.strip() for t in tasks.split(",") if t.strip()]
    # Keep task_done for existing tasks; pad with False for new tasks
    old_task_done = pet.task_done[:]
    pet.task_done = [old_task_done[i] if i < len(old_task_done) else False for i in range(len(task_list))]
    
    pet.name = name
    pet.age = int(age)
    pet.species = species
    pet.care_tasks = task_list

    return taskview(state, pet.id)


@route("/toggletask/<pet_id>/<task_index>")
def toggletask(state: State, pet_id: str, task_index: str) -> Page:
    # Convert to integer
    task_index = int(task_index)
    pet = next((p for p in state.pet_list if p.id == pet_id), None)
    if not pet:
        return Page(state, ["Pet not found."])
    
    # Toggle task completion
    pet.task_done[task_index] = not pet.task_done[task_index]
    return taskview(state, pet_id)

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


start_server(State())
