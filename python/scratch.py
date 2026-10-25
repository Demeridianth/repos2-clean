from dataclasses import dataclass
from random import choice


task_db = ['task1', 'task2', 'task3', 'task4', 'task5', 'task6', 'task7', 'task8', 'task9', 'task10']


@dataclass
class Student:
    username: str
    email: str
    password: str
    authenticated: bool = False


john = Student('John', 'john@gmail.com', '123', True)
sarah = Student('Sarah', 'sarah@gmail.com', '234', False)
students = [john, sarah]


def get_student(name: str):
    return next((student for student in students if name == student.username), None)


if __name__ == '__main__':
    while True:
        name = input('enter student name: ')
        student = get_student(name)

        if student is None:
            print('no such student in db')
        elif student.authenticated:
            print(f'{student.username} gets {choice(task_db)}')
        else:
            print('no authentication')
    