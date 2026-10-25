import pytest
from scratch import Student, get_student, students


def test_existing_students():
    student = get_student('John')
    assert student is not None
    assert student.username == 'John'


def test_nonexisting_students():
    student = get_student('Bob')
    assert student is None