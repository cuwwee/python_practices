#positioal only args
def my_function(name, /):
  print("Hello", name)

my_function("Emil")

#keyword only args
def my_function(*, name):
  print("Hello", name)

my_function(name = "Emil")

#combine
def my_function(a, b, /, *, c, d):
  return a + b + c + d

result = my_function(5, 10, c = 15, d = 20)
print(result)