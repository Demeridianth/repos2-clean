data = [
    {'id': 123, 'name': 'Bob', 'position': 'manager'},
    {'id': 456, 'name': 'Joe', 'position': 'assitent manager'},
    {'id': 789, 'name': 'Anna', 'position': 'agent'}
]

def search_data(id: int | None = None, name: str | None = None, position: str | None = None):
    def check_data(record: dict):
        return all(
            (
                id is None or record['id'] == id,
                name is None or record['name'] == name,
                position is None or record['position'] == position
            )
        )
    result = [record for record in data if check_data(record)]
    return result

print(search_data(123))