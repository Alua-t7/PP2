#1 convert degree to radian
import math

degree = float(input("Input degree: "))
radian = math.radians(degree) 
print(f"Output radian: {radian:.6f}")

#2 Area of a trapezoid
height = float(input("Height: "))
base1 = float(input("Base, first value: "))
base2 = float(input("Base, second value: "))

area = 0.5 * (base1 + base2) * height
print("Expected Output:", area)

#3 Area of a regular polygon
import math

n = int(input("Input number of sides: "))
side = float(input("Input the length of a side: "))


area = (n * side ** 2) / (4 * math.tan(math.pi / n))
print(f"The area of the polygon is: {area}")

#4 Area of a parallelogram
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))

area = base * height
print("Expected Output:", area)