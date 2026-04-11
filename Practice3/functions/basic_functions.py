#1
def myFunction():
    print("Hello from a function")
myFunction()
myFunction()
myFunction()

#2
def fahhrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9
print(fahhrenheit_to_celsius(77))
print(fahhrenheit_to_celsius(95))
print(fahhrenheit_to_celsius(50))

#3
def get_greeting():
    return "Hello from a function"

message = get_greeting()
print(message)

#4
def get_greeting():
    return "Hello from a function"

print(get_greeting())

#5
def my_function():
    pass