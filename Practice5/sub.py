import re

s = input()
x = re.sub(r"[,]", ".", s)
print(x)