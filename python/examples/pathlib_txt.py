from pathlib import Path

path = Path(r'C:\Users\user\Desktop\lists\games.txt')

with path.open() as file:
    games = file.read().splitlines()
    games = list(dict.fromkeys(games))

new_path = Path(r'C:\Users\user\Desktop\lists\unique_games.txt')

with new_path.open('w') as file:
    for game in games:
        file.write(f'{game}\n')


