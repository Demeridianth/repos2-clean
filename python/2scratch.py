nums = [2, 7, 11, 17]


def twosum(nums, target):
    for n in range(len(nums)):
        for j in range(n + 1, len(nums)):
            if nums[n] + nums[j] == target:
                return [n, j]
        
