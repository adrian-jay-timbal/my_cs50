# cs50 library for get_int
from cs50 import get_int

# prompt user again and again
# until positive integer not > 8
number = 0
while number <= 0 or number > 8:
    number = get_int("Height: ")

# loops and print '#' in each corresponding line
for r in range(number):
    for c in range(number):
        # check what column to print
        if c >= number - (r + 1):
            print("#", end="")
        else:
            print(" ", end="")

    # the 2 spaces in between
    print("  ", end="")

    # the right side blocks
    for c in range(r + 1):
        print("#", end="")

    # next line at the end without doubling
    print("\n", end="")
