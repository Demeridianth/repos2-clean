import json 
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os

app = FastAPI(title='Staff Management Api')

# ------------------------------
# Models
# ------------------------------

class StaffMember(BaseModel):
    name: str
    password: int
    account_type: str

class StaffUpdateUser(BaseModel):
    name: Optional[str]
    password: Optional[str]


# ------------------------------
# Repository for JSON storage
# ------------------------------

class JsonRepository:
    def __init__(self, filename='staff_members.json'):
        self.filename = filename
        if not os.path.exists(filename):
            self.write_to_file([])

    def read_from_file(self):
        if not os.path.exists(self.filename):
            self.write_to_file([])
            return []
        with open(self.filename, 'r') as data:
            try:
                return json.load(data)
            except json.JSONDecodeError:
                return []

    def write_to_file(self, staff_data):
        with open(self.filename, 'w') as file:
            json.dump(staff_data, file, indent=4)

repo = JsonRepository()


# ------------------------------
# Helper functions
# ------------------------------

def get_all_staff():
    return repo.read_from_file()

def save_all_staff(staff_list):
    return repo.write_to_file(staff_list)

def find_member_by_name(name):
    staff_list = get_all_staff()
    for member in staff_list:
        if member['name'] == name:
            return member
    return None


# ------------------------------
# Admin Endpoints
# ------------------------------

@app.post('/admin/staff', response_model=StaffMember)
def add_staff_member(member: StaffMember, admin_password: str):
    if admin_password != 'admin':
        raise HTTPException(status_code=401, detail='Unauthorized')
    if find_member_by_name(member.name):
        raise HTTPException(status_code=400, detail='Staff member already exists')
    staff_list = get_all_staff()
    staff_list.append(member.model_dump())
    save_all_staff(staff_list)
    return member

@app.get('/admin/staff', response_model=List[StaffMember])
def list_staff_members(admin_password: str):
    if admin_password != 'admin':
        raise HTTPException(status_code=401, detail='Unauthorized')
    return get_all_staff()

@app.put('/admin/staff/{name}', response_model=StaffMember)
def edit_staff(name: str, updated_member: StaffMember, admin_password):
    if admin_password != 'admin':
        raise HTTPException(status_code=401, detail='Unauthorized')
    staff_list = get_all_staff()
    for i, staff_member in enumerate(staff_list):
        if staff_member['name'] == name:
            staff_list[i] = updated_member.model_dump(exclude_unset=True)
            save_all_staff(staff_list)
            return updated_member
    raise HTTPException(status_code=404, detail='Staff memmber not found')

@app.delete('/admin/staff/{name}', response_model=StaffMember)
def delete_staff(name: str, admin_password):
    if admin_password != 'admin':
        raise HTTPException(status_code=401, detail='Unautharizes')
    staff_list = get_all_staff()
    for staff_member in staff_list:
        if staff_member['name'] == name:
            staff_list.remove(staff_member)
            save_all_staff(staff_list)
            return staff_member
    raise HTTPException(status_code=404, detail='Staff member not found')


# ------------------------------
# User Endpoints
# ------------------------------

@app.get('/user/{password}', response_model=StaffMember)
def list_user(name: str):
    staff_list = get_all_staff()
    for staff_member in staff_list:
        if staff_member['name'] == name:
            return staff_member
    raise HTTPException(status_code=404, detail='Staff member not found')

@app.put('/user/{password}', response_model=StaffMember)
def edit_staff(password: int, updated_member: StaffUpdateUser):
    staff_list = get_all_staff()
    for i, staff_member in enumerate(staff_list):
        if staff_member['password'] == password:
            if updated_member.name is not None:
                staff_list[i]['name'] = updated_member.name
            if updated_member.password is not None:
                staff_list[i]['password'] = updated_member.password
            save_all_staff(staff_list)
            return staff_list[i]
    raise HTTPException(status_code=404, detail='Staff member not found')

