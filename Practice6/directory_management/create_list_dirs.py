import os

os.makedirs("test_dir/sub_dir", exist_ok=True)

print("Directories created.")

items = os.listdir(".")

print("Files and folders in current directory:")
for item in items:
    print(item)

print("\nPython files:")
for file in items:
    if file.endswith(".py"):
        print(file)