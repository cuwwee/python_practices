import math

# 1. Write a Python program to convert degree to radian.
degree = float(input("Input degree: "))
radian = math.radians(degree)
print(f"Output radian: {radian:.6f}")
print()


# 2. Write a Python program to calculate the area of a trapezoid.
height = float(input("Height: "))
base1 = float(input("Base, first value: "))
base2 = float(input("Base, second value: "))
trapezoid = 0.5 * (base1 + base2) * height
print(f"Expected Output: {trapezoid}")
print()


# 3. Write a Python program to calculate the area of regular polygon.
side = int(input("Input number of sides: "))
length = float(input("Input the length of a side: "))
# Formula: (n * s^2) / (4 * tan(pi/n))
polygon = (side * length ** 2) / (4 * math.tan(math.pi /side))
print(f"The area of the polygon is: {polygon}")
print()


# 4. Write a Python program to calculate the area of a parallelogram.
base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))
parallelogram = base * height
print(f"Expected Output: {parallelogram}")