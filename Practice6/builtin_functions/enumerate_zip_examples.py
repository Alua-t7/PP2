#enumerate
names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

print("Using enumerate:")
for index, name in enumerate(names):
    print(index, name)

#zip
print("\nUsing zip:")
for name, score in zip(names, scores):
    print(name, score)

value = "123"

#type()
print("\nType before:", type(value))

number = int(value)

print("Converted value:", number)
print("Type after:", type(number))