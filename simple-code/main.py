from logger import timer

@timer
def display_age(age):
    print("My age is", age, "years old.")

display_age(25)