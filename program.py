def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Get user input

nums = list(map(int, input("Enter a list of numbers: ").split()))
target = int(input("Enter a target number: "))


result = two_sum(nums, target)

# Print the result
print(two_sum(nums, target))
print("Indices: ", result)