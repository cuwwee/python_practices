import re

s = input()
x = re.findall(r"[A-Z][a-z]+", s)
print(x)