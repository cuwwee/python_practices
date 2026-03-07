import re

s = "Hello world!"
x = re.search(r"^H.*r", s)
if x:
    print(x.group())