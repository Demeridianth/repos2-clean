from dataclasses import dataclass


class Employee:
    id: int
    name: str
    position: str
    salary: float

class Staff:
    def __init__(self):
        self.staff_list = []

    def get_all_staff(self):
        return self.staff_list
    
class ConsoleInterface:
    @staticmethod
    def get_user_input(prompt, converter: str):
        return converter(input(prompt))
    
    