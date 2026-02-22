#1 squares of numbers up to some number N
def square_generator(n):
    for i in range(1, n + 1):
        yield i * i

n = int(input())

for value in square_generator(n):
    print(value)

#2 even numbers between 0 and n
def even_generator(n):
    for i in range(0, n + 1, 2):
        yield i

n = int(input())

first = True
for num in even_generator(n):
    if not first:
        print(",", end="")
    print(num, end="")
    first = False

#3 divisible by 3 and 4
def divisible_by_3_and_4(n):
    for i in range(0, n + 1, 12):
        yield i

n = int(input())

first = True
for num in divisible_by_3_and_4(n):
    if not first:
        print(" ", end="")
    print(num, end="")
    first = False

#4 square of all numbers from (a) to (b)
def square_generator(a, b):
    for i in range(a, b + 1):
        yield i * i

a, b = map(int, input().split())

for value in square_generator(a, b):
    print(value)

#5 all numbers from (n) down to 0
def countdown(n):
    for i in range(n, -1, -1):
        yield i

n = int(input())

for number in countdown(n):
    print(number)


