from typing import Optional


class Collection:
    def __init__(self, items: Optional[list] = None):
        self.items = items or []


# nums = ['a', 'b', 'c', 'c']
# dict_nums = dict.fromkeys(nums)
# print(dict_nums)

nums = [1, 2, 2, 3]
unique_nums = []

for n in nums:
    if n not in unique_nums:
        unique_nums.append(n)

print(unique_nums)

