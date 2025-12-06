from dataclasses import dataclass, field
from drafter import *
import re

# ------------------------------------------
# WEBSITE INFORMATION
# ------------------------------------------

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

# ------------------------------------------
# SLUG FUNCTION
# ------------------------------------------

def slugify(name: str) -> str:
    """Convert a pet name into a URL-safe slug."""
    slug = name.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)  # Remove all non-URL-safe chars
    return slug


# ------------------------------------------
# DATA MODELS
# ------------------------------------------

@dataclass
class Pet:
    name: str
    age: int
    species: str
    care_tasks: list[str]
    task_done: list[bool]
    slug: str  # URL-safe unique identifier


@dataclass
class State:
    pet_list: list[Pet] = field(default_factory=list)


# ------------------------------------------
# INDEX (ADD PET)
# ------------------------------------------

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
    slug = slugify(name)

    pet = Pet(
        name=name,
        age=int(age),
        species=species,
        care_tasks=task_list,
        task_done=[False] * len(task_list),
        slug=slug
    )

    state.pet_list.append(pet)
    return petview(state)


# ------------------------------------------
# MAIN PET LIST
# ------------------------------------------

@route
def petview(state: State) -> Page:
    if not state.pet_list:
        return index(state)

    elements = ["View your pets' pages below:"]

    for pet in state.pet_list:
        status = "✅ All tasks done!" if all(pet.task_done) else "❌ Tasks remaining"
        elements.append(f"{pet.name} - {status}")
        elements.append(Button(f"View Tasks for {pet.name}", f"/taskview/{pet.slug}"))

    elements.append(Button("Add New Pet", "/new_pet"))
    return Page(state, elements)


# ------------------------------------------
# TASK VIEW PAGE
# ------------------------------------------

@route("/taskview/<slug>")
def taskview(state: State, slug: str) -> Page:
    pet = next((p for p in state.pet_list if p.slug == slug), None)
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
        content.append(Button(f"Toggle Task {i}", f"/toggletask/{pet.slug}/{i}"))

    content.append(Button("Edit Pet", f"/editpet/{pet.slug}"))
    content.append(Button("Delete Pet", f"/deletepet/{pet.slug}"))
    content.append(Button("Return to Main Page", "/petview"))

    return Page(state, content)


# ------------------------------------------
# DELETE PET
# ------------------------------------------

@route("/deletepet/<slug>")
def deletepet(state: State, slug: str) -> Page:
    state.pet_list = [p for p in state.pet_list if p.slug != slug]
    return petview(state)


# ------------------------------------------
# EDIT PET
# ------------------------------------------

@route("/editpet/<slug>")
def editpet(state: State, slug: str) -> Page:
    pet = next((p for p in state.pet_list if p.slug == slug), None)
    if not pet:
        return Page(state, ["Pet not found."])

    return Page(state, [
        "Edit Pet Information:",
        "Name:", TextBox("name", pet.name),
        "Age:", TextBox("age", str(pet.age)),
        "Species:", TextBox("species", pet.species),
        "Tasks (comma separated):", TextBox("tasks", ", ".join(pet.care_tasks)),
        Button("Save Changes", f"/savepet/{pet.slug}"),
        Button("Cancel", f"/taskview/{pet.slug}")
    ])


# ------------------------------------------
# SAVE EDITED PET
# ------------------------------------------

@route("/savepet/<slug>")
def savepet(state: State, slug: str, name: str, age: str, species: str, tasks: str) -> Page:
    pet = next((p for p in state.pet_list if p.slug == slug), None)
    if not pet:
        return Page(state, ["Pet not found."])

    task_list = [t.strip() for t in tasks.split(",") if t.strip()]
    old_task_done = pet.task_done[:]

    pet.task_done = [
        old_task_done[i] if i < len(old_task_done) else False
        for i in range(len(task_list))
    ]

    pet.name = name
    pet.age = int(age)
    pet.species = species
    pet.care_tasks = task_list

    # NEW: Regenerate slug if name changed
    pet.slug = slugify(name)

    return taskview(state, pet.slug)


# ------------------------------------------
# TOGGLE TASK
# ------------------------------------------

@route("/toggletask/<slug>/<task_index>")
def toggletask(state: State, slug: str, task_index: str) -> Page:
    pet = next((p for p in state.pet_list if p.slug == slug), None)
    if not pet:
        return Page(state, ["Pet not found."])

    i = int(task_index)
    pet.task_done[i] = not pet.task_done[i]

    return taskview(state, slug)


# ------------------------------------------
# NEW PET PAGE
# ------------------------------------------

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


# ------------------------------------------
# START SERVER
# ------------------------------------------

start_server(State())
