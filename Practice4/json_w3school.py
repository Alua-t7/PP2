#1
import json
x = '{"name":"John", "age":30, "city":"New York"}'

y = json.loads(x)

# the result is a Python dictionary:
print(y["age"])

#2
import json

x = {
  "name": "John",
  "age": 30,
  "city": "New York"
}

y = json.dumps(x)

# the result is a JSON string:
print(y)

#3
import json

print(json.dumps({"name":"John", "age":30}))
print(json.dumps(["apple", "bananas"]))
print(json.dumps(("apple", "bananas")))
print(json.dumps("hello"))
print(json.dumps(42))
print(json.dumps(31.76))
print(json.dumps(True))
print(json.dumps(False))
print(json.dumps(None))

#4
import json

x = {
    "name":"John",
    "age": 30,
    "married": True,
    "divorced": False,
    "children": ("Ann", "Billy"),
    "pets": None,
    "cars": [
        {"model": "BMW 230", "mpg": 27.5},
        {"model": "Ford Edge", "mpg": 24.1}
    ]
}

print(json.dumps(x))

#5
json.dumps(x, indent=4)

json.dumps(x, indent=4, separators = (". ", "="))

json.dumps(x, indent=4, sort_keys=True)
