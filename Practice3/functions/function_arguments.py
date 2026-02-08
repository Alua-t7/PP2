#1
def my_function(fname):
    print(fname + "Refsnes")

my_function("Emil")
my_function("Tobias")
my_function("Linus")


#2
def my_function(name):  #name is a parameter
    print("Hello", name)

my_function("Emil")     #"Emil" is an argument

#3
def myFunction(fname, lname):
    print(fname + " " + lname)

myFunction("Emil", "Refsnes")


#4
def my_function(name = "frend"):
    print("Hello", name)

my_function("Emil")
my_function("Tobias")
my_function()
my_function("Linus")

#5
def my_function(country = "Norway"):
    print("I am from", country)

my_function("Sweden")
my_function("India")
my_function()
my_function("Brazil")

#6
def myFunction(animal, name):
    print("I have a ", animal)
    print("My", animal + "'s name is", name)

myFunction(animal = "dog", name = "Buddy")


#7
def my_function(animal, name):
    print("I have a", animal)
    print("My", animal + "'s name is", name)

my_function("dog", "Buddy")

#8
def my_function(animal, name, age):
    print("I have a ", age, "year old", animal, "named", name)

my_function("dog", name = "Buddy", age = 5)


#9
def my_function(fruits):
    for fruit in fruits:
        print(fruit)

my_fruits = ["apple", "banana", "cherry"]
my_function(my_fruits)

#10
def my_function(person):
    print("Name:", person["name"])
    print("Age:", person["age"])

my_person = {"name" : "Emil", "age": 25}
my_function(my_person)
 

#11
def my_function(name, /):
    print("Hello", name)

my_function("Emil")

#12
def my_function(*, name):
    print("Hello", name)

my_function(name = "Emil")


#13
def myFunction(a, b, / , *, c, d):
    return a + b + c + d

result = myFunction(5, 10, c = 15, d = 20)
