#create and write sample data
with open("sample.txt", "w") as file:
    file.write("Hello, this is the first line.\n")
    file.write("Python file handling practice.\n")

print("File created and data written")

#append new lines
with open("sample.txt", "a") as file:
    file.write("this line was appended later.\n")
    file.write("Learning Python is fun!\n")

print("New lines appended")