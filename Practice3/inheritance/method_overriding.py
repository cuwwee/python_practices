class Animal:
    def speak(self):
        print("Animal makes a sound")

class Dog(Animal):
    def speak(self):   # overriding
        print("Dog barks")

a = Animal()
d = Dog()

a.speak()
d.speak()