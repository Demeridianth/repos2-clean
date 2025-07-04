from dataclasses import dataclass
import json


@dataclass
class Employee:
    id: int 
    name: str
    age: int


class Staff:
    def __init__(self):
        self.staff_members = {}

    @staticmethod
    def get_user_input(prompt: str, converter=str):
        return converter(input(prompt))

    def add_employee(self):
        name = self.get_user_input('enter name: ')
        age = self.get_user_input('enter age: ', int)
        id = max(self.staff_members.keys(), default=0) + 1
        new_employee = Employee(name=name, age=age, id=id)
        self.staff_members[new_employee.id] = new_employee

    def get_all_employees(self):
        return self.staff_members
    
class JsonRepository:
    def __init__(self, file_path):
        self.file_path = file_path

    def write_to_file(self, database):
        with open(self.file_path, 'w') as file:
            file.write(json.dumps(database))

    def read_from_file(self):
        with open(self.file_path, 'r') as file:
            return json.loads(file.read())

staff = Staff()
staff.add_employee()
print(staff.get_all_employees())
