from functools import reduce

numbers = [1, 2, 3, 4, 5, 6]

#map()
squared = list(map(lambda x: x**2, numbers))
print("Squared:", squared)

#filter()
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", evens)

#reduce()
total = reduce(lambda x, y: x + y, numbers)
print("Sum:", total)