# 1. Squares up to n
def square(n):
    for i in range(1, n + 1):
        yield i ** 2

n = int(input("1. Enter a number: "))
print("Squares up to n:", list(square(n)))
print()


# 2. Even number up to n
def even_numbers(n):
    for i in range(0, n + 1):
        if i % 2 == 0:
            yield i

n = int(input("2. Enter a numner: "))
even_list = [str(num) for num in even_numbers(n)]
print("Even numbers:", ", ".join(even_list))
print()


# 3. Divisible by 3 and 4
def divisible(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input("3. Enter a number: "))
print("Numbers divisible to 3, 4:", list(divisible(n)))
print()


# 4. Squares from a to b
def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

a = int(input("4. Start: "))
b = int(input("   End: "))
print("Squares:")
for i in squares(a, b):
    print(i)
print()


# 5. Countdown
def countdown(n):
    for i in range(n, -1, -1):
        yield i

n = int(input("5. Enter a number: "))
print("Countdown:")
for i in countdown(n):
    print(i)