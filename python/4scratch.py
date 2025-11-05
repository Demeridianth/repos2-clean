from pathlib import Path

path = Path(r'C\User\myfolder\file.txt')

with path.open() as file:
    books_to_read = file.read().splitlines()
    books_to_read = list(dict.fromkeys(books_to_read))

with path.open('w') as file:
    for book in books_to_read():
        file.write(f'book\n')