from pathlib import Path

path = Path(r'C:\test\books.txt')

with path.open() as file:
    books = file.read().splitlines()
    books_clean = list(dict.fromkeys(books))

with path.open('w') as file:
    for book in books_clean:
        file.write(f'{book}\n')
