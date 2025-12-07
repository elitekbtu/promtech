import enum

class PriorityLevel(str, enum.Enum):
    high = "высокий"
    medium = "средний"
    low = "низкий"

try:
    print(f"Lookup by name 'high': {PriorityLevel['high']}")
except KeyError:
    print("Lookup by name 'high' failed")

try:
    print(f"Lookup by value 'высокий': {PriorityLevel('высокий')}")
except ValueError:
    print("Lookup by value 'высокий' failed")

try:
    print(f"Lookup by name 'высокий': {PriorityLevel['высокий']}")
except KeyError:
    print("Lookup by name 'высокий' failed")
