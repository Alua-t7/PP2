#1
print("Hello")
print('Hello')

#2
print("It's alright")
print("He is called 'Johnny'")
print('He is called "Johnny"')

#3
a = "Hello"
print(a)

#4
a = """Lorem ipsum dolor sit amet,
consectetur adipiscing elit,
sed do eiusmod tempor incididunt
ut labore et dolore magna aliqua."""
print(a)

#5
a = "Hello, World!"
print(a[1])

#6
for x in "banana":
  print(x)

#7
a = "Hello, World!"
print(len(a))

#8
txt = "The best things in life are free!"
print("free" in txt)

#9
txt = "The best things in life are free!"
if "free" in txt:
  print("Yes, 'free' is present.")

#10
txt = "The best things in life are free!"
print("expensive" not in txt)

#11
txt = "The best things in life are free!"
if "expensive" not in txt:
  print("No, 'expensive' is NOT present.")

#12
b = "Hello, World!"
print(b[2:5])

#13
b = "Hello, World!"
print(b[:5])

#14
b = "Hello, World!"
print(b[2:])

#15
b = "Hello, World!"
print(b[-5:-2])

#16
a = "Hello, World!"
print(a.upper())

#17
a = "Hello, World!"
print(a.lower())

#18
a = " Hello, World! "
print(a.strip()) # returns "Hello, World!"

#19
a = "Hello, World!"
print(a.replace("H", "J"))

#20
a = "Hello, World!"
print(a.split(",")) # returns ['Hello', ' World!']

#21
a = "Hello"
b = "World"
c = a + b
print(c)

#22
a = "Hello"
b = "World"
c = a + " " + b
print(c)

#23
age = 36
txt = f"My name is John, I am {age}"
print(txt)

#24
price = 59
txt = f"The price is {price} dollars"
print(txt)

#25
price = 59
txt = f"The price is {price:.2f} dollars"
print(txt)

#26
txt = f"The price is {20 * 59} dollars"
print(txt)

#27
txt = "We are the so-called \"Vikings\" from the north."

#28

