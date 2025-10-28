import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Staff Management API")

# ------------------------------
# Models
# ------------------------------

class StaffMember(BaseModel):
    name: str
    password: str
    account_type: str

# For updating user (password only or name + password)
class StaffUpdateUser(BaseModel):
    name: Optional[str]
    password: Optional[str]

# ------------------------------
# Repository for JSON storage
# ------------------------------

class JsonRepository:
    def __init__(self, filename="staff_members.json"):
        self.filename = filename
        if not os.path.exists(filename):
            self.write_to_file([])

    def write_to_file(self, staff_data):
        with open(self.filename, 'w') as f:
            json.dump(staff_data, f, indent=4)

    def read_from_file(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

repo = JsonRepository()

# ------------------------------
# Helper functions
# ------------------------------

def get_all_staff():
    return repo.read_from_file()

def save_all_staff(staff_list):
    repo.write_to_file(staff_list)

def find_member_by_name(name):
    staff_list = get_all_staff()
    for member in staff_list:
        if member['name'] == name:
            return member
    return None

# ------------------------------
# Admin Endpoints
# ------------------------------

@app.get("/admin/staff", response_model=List[StaffMember])
def list_staff(admin_password: str):
    if admin_password != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_all_staff()

@app.post("/admin/staff", response_model=StaffMember)
def add_staff(member: StaffMember, admin_password: str):
    if admin_password != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    staff_list = get_all_staff()
    if find_member_by_name(member.name):
        raise HTTPException(status_code=400, detail="Staff member already exists")
    staff_list.append(member.dict())
    save_all_staff(staff_list)
    return member

@app.put("/admin/staff/{name}", response_model=StaffMember)
def edit_staff(name: str, updated_member: StaffMember, admin_password: str):
    if admin_password != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    staff_list = get_all_staff()
    for i, member in enumerate(staff_list):
        if member['name'] == name:
            staff_list[i] = updated_member.dict()
            save_all_staff(staff_list)
            return updated_member
    raise HTTPException(status_code=404, detail="Staff member not found")

@app.delete("/admin/staff/{name}")
def delete_staff(name: str, admin_password: str):
    if admin_password != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    staff_list = get_all_staff()
    for member in staff_list:
        if member['name'] == name:
            staff_list.remove(member)
            save_all_staff(staff_list)
            return {"detail": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="Staff member not found")

# ------------------------------
# User Endpoints
# ------------------------------

@app.get("/user/{password}", response_model=StaffMember)
def get_user_details(password: str):
    staff_list = get_all_staff()
    for member in staff_list:
        if member['password'] == password:
            return member
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/user/{password}", response_model=StaffMember)
def update_user(password: str, update: StaffUpdateUser):
    staff_list = get_all_staff()
    for i, member in enumerate(staff_list):
        if member['password'] == password:
            if update.name:
                staff_list[i]['name'] = update.name
            if update.password:
                staff_list[i]['password'] = update.password
            save_all_staff(staff_list)
            return staff_list[i]
    raise HTTPException(status_code=404, detail="User not found")
