import json
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt      # exta security | token
from datetime import datetime, timedelta

# ------------------------------
# App setup
# ------------------------------
app = FastAPI(title="Staff Management API")

# For token generation
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ------------------------------
# Models
# ------------------------------
class StaffMember(BaseModel):
    name: str
    hashed_password: str
    account_type: str  # "admin" or "user"

class StaffCreate(BaseModel):
    name: str
    password: str
    account_type: str

class StaffUpdate(BaseModel):
    name: Optional[str]
    password: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str

# ------------------------------
# JSON Repository
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
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(name: str, password: str):
    staff_list = repo.read_from_file()
    for member in staff_list:
        if member["name"] == name and verify_password(password, member["hashed_password"]):
            return member
    return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = find_member_by_name(name)
    if user is None:
        raise credentials_exception
    return user

def find_member_by_name(name: str):
    staff_list = repo.read_from_file()
    for member in staff_list:
        if member["name"] == name:
            return member
    return None

def save_all_staff(staff_list):
    repo.write_to_file(staff_list)

# ------------------------------
# Authentication endpoint
# ------------------------------
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["name"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ------------------------------
# Admin Endpoints
# ------------------------------
@app.get("/admin/staff", response_model=List[StaffMember])
def list_staff(current_user: dict = Depends(get_current_user)):
    if current_user["account_type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return repo.read_from_file()

@app.post("/admin/staff", response_model=StaffMember)
def add_staff(member: StaffCreate, current_user: dict = Depends(get_current_user)):
    if current_user["account_type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    staff_list = repo.read_from_file()
    if find_member_by_name(member.name):
        raise HTTPException(status_code=400, detail="Staff member already exists")
    hashed_password = get_password_hash(member.password)
    new_member = {"name": member.name, "hashed_password": hashed_password, "account_type": member.account_type}
    staff_list.append(new_member)
    save_all_staff(staff_list)
    return new_member

@app.put("/admin/staff/{name}", response_model=StaffMember)
def edit_staff(name: str, update: StaffUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["account_type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    staff_list = repo.read_from_file()
    for i, member in enumerate(staff_list):
        if member["name"] == name:
            if update.name:
                staff_list[i]["name"] = update.name
            if update.password:
                staff_list[i]["hashed_password"] = get_password_hash(update.password)
            save_all_staff(staff_list)
            return staff_list[i]
    raise HTTPException(status_code=404, detail="Staff member not found")

@app.delete("/admin/staff/{name}")
def delete_staff(name: str, current_user: dict = Depends(get_current_user)):
    if current_user["account_type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    staff_list = repo.read_from_file()
    for member in staff_list:
        if member["name"] == name:
            staff_list.remove(member)
            save_all_staff(staff_list)
            return {"detail": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="Staff member not found")

# ------------------------------
# User Endpoints
# ------------------------------
@app.get("/user/me", response_model=StaffMember)
def get_my_details(current_user: dict = Depends(get_current_user)):
    return current_user

@app.put("/user/me", response_model=StaffMember)
def update_my_details(update: StaffUpdate, current_user: dict = Depends(get_current_user)):
    staff_list = repo.read_from_file()
    for i, member in enumerate(staff_list):
        if member["name"] == current_user["name"]:
            if update.name:
                staff_list[i]["name"] = update.name
            if update.password:
                staff_list[i]["hashed_password"] = get_password_hash(update.password)
            save_all_staff(staff_list)
            return staff_list[i]
    raise HTTPException(status_code=404, detail="User not found")
