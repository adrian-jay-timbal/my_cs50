//libraries used
#include <stdio.h>
#include <cs50.h>

//functions prototype
void valid(void);
long get_len(long num);
long main_algorithm(long number);

//main program execution
int main(void)
{
    valid();
}

// gets user inputs and performs the validation of the input.
void valid(void)
{
    long card_num;
    do
    {
        card_num = get_long("Enter Card Number: ");

        //if the number is invalid it prints INVALID.
        if ((get_len(card_num) != 13) && (get_len(card_num) != 15) && (get_len(card_num) != 16))
        {
            printf("INVALID\n");
        }
        //if valid it executes Luhn's Algorithm to check the card
        else
        {
            main_algorithm(card_num);
        }
    }
    while (get_len(card_num) <= 0);
}

//this identifies the length of the number that the user gave.
long get_len(long num)
{
    long len = 0;
    while (num > 0)
    {
        num /= 10;
        len++;
    }
    return len;
}

//this is the Luhn's Algorithm
long main_algorithm(long number)
{
    long valid_card = number;
    int sum = 0;
    long split = 10;

    //iterates from the first digit to every other digits
    //and adding it to the variable sum.
    while (valid_card > 0)
    {
        int last_num = valid_card % 10;
        sum = sum + last_num;
        valid_card = valid_card / 100;

    }
    //iterates from the second digit to every other digits
    //and multiply it by 2 and adding it to the variable sum.
    valid_card = number / 10;
    while (valid_card > 0)
    {
        int last_num = valid_card % 10;
        int double_num = last_num * 2;
        sum = sum + (double_num / 10) + (double_num % 10);
        valid_card = valid_card / 100;
    }

    //iterates through the card number
    //to get the divisor that will be used
    //to extract the first digit and the first and second digit of the card.
    valid_card = number;
    for (int i = 0; i < get_len(valid_card) - 2; i++)
    {
        split = split * 10;
    }

    //extraction of the first digit and the first and second digit of the card.
    int digit_one = valid_card / split;
    int digit_two = valid_card / (split / 10);

    //this checks if the computation is correct and print the brandname of the card.
    if (sum % 10 == 0)
    {
        if (digit_two == 34 || digit_two == 37)
        {
            printf("AMEX\n");
        }
        else if (digit_two > 50 && digit_two < 56)
        {
            printf("MASTERCARD\n");
        }
        else if (digit_one == 4)
        {
            printf("VISA\n");
        }
        else
        {
            printf("INVALID\n");
        }
    }
    else
    {
        printf("INVALID\n");
    }

    return 0;
}
