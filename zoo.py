class Food:
    def __init__(self, name):
        self.name = name


class Animal:
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self.hungry = True

    def eat(self, food):
        raise NotImplementedError


class Carnivore(Animal):
    def eat(self, food):
        if not self.hungry:
            print(self.name, "is not hungry")
            return

        if food.name == "Meat":
            print(self.name, "eats meat")
            self.hungry = False
        else:
            print(self.name, "does not eat", food.name)


class Herbivore(Animal):
    def eat(self, food):
        if not self.hungry:
            print(self.name, "is not hungry")
            return

        if food.name in ("Grass", "Fruit"):
            print(self.name, "eats", food.name)
            self.hungry = False
        else:
            print(self.name, "does not eat", food.name)


class Cage:
    def __init__(self, number):
        self.number = number
        self.animals = []

    def add_animal(self, animal):
        self.animals.append(animal)
        print(animal.name, "added to cage", self.number)


class Worker:
    def __init__(self, name):
        self.name = name

    def feed(self, animals, food):
        print(self.name, "feeds animals with", food.name)
        for animal in animals:
            animal.eat(food)


meat = Food("Meat")
grass = Food("Grass")

lion = Carnivore("Simba", "Lion")
cow = Herbivore("Burenka", "Cow")

cage1 = Cage(1)
cage1.add_animal(lion)
cage1.add_animal(cow)

worker = Worker("Aram")
worker.feed(cage1.animals, grass)
worker.feed(cage1.animals, meat)