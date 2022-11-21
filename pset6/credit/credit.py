from cs50 import get_int

number = 0

# gets user inputs and performs the validation of the input.
while number <= 0:
    number = get_int("Number: ")
size = len(str(number))


# this is the implimentation of Luhn's Algorithm
def main():
    valid_card = number
    n_sum = 0
    split = 10

    # iterates from the first digit to every other digits
    # and adding it to the variable sum.
    while valid_card > 0:
        last_num = valid_card % 10
        n_sum += last_num
        valid_card //= 100

    # iterates from the second digit to every other digits
    # and multiply it by 2 and adding it to the variable sum.
    valid_card = number // 10
    while valid_card > 0:
        last_num = valid_card % 10
        double_num = last_num * 2
        n_sum += (double_num // 10) + (double_num % 10)
        valid_card //= 100

    # iterates through the card number
    # to get the divisor that will be used
    # to extract the first digit and the first and second digit of the card.
    valid_card = number
    for i in range(size - 2):
        split *= 10

    # extraction of the first digit and the first and second digit of the card.
    digit_one = valid_card // split
    digit_two = valid_card // (split // 10)

    # this checks if the computation is correct and print the brandname of the card.
    if n_sum % 10 == 0:
        if digit_two == 34 or digit_two == 37:
            print("AMEX")
        elif digit_two > 50 and digit_two < 56:
            print("MASTERCARD")
        elif digit_one == 4:
            print("VISA")
        else:
            print("INVALID")
    else:
        print("INVALID")


# main program execution
if size == 13 or size == 15 or size == 16:
    main()
else:
    print("INVALID")
