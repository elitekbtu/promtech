import enum

class PriorityLevel(str, enum.Enum):
    high = "высокий"
    medium = "средний"
    low = "низкий"

counts = {
    "high": 0,
    "medium": 0,
    "low": 0
}

# Simulate database result
result = [
    (PriorityLevel.high, 10),
    (PriorityLevel.medium, 5),
    (PriorityLevel.low, 2)
]

print("--- Using .value ---")
counts_value = counts.copy()
for priority_level, count in result:
    print(f"Key: {priority_level.value}, Count: {count}")
    counts_value[priority_level.value] = count

print(f"Counts dict: {counts_value}")
print(f"Accessing 'high': {counts_value.get('high', 0)}")

print("\n--- Using .name ---")
counts_name = counts.copy()
for priority_level, count in result:
    print(f"Key: {priority_level.name}, Count: {count}")
    counts_name[priority_level.name] = count

print(f"Counts dict: {counts_name}")
print(f"Accessing 'high': {counts_name.get('high', 0)}")
