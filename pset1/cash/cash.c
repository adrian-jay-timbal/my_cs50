//libraries needed.
#include <stdio.h>
#include <cs50.h>
#include <math.h>

int main(void)
{
    //get the input from the user.
    float change;
    do
    {
        change = get_float("Change owed: ");
    }
    while (change < 0);

    //this rounds the input by using the round() function on math.h library.
    int cents = round(change * 100);
    int coins = 0;

    //this substract every amount of the coins that is valid through conditions
    //and add it to the variable coins to determine the number of coins needed.
    while (cents != 0)
    {
        if (cents >= 25)
        {
            cents = cents - 25;
            coins++;
        }
        else if ((cents < 25) && (cents >= 10))
        {
            cents = cents - 10;
            coins++;
        }
        else if ((cents < 10) && (cents >= 5))
        {
            cents = cents - 5;
            coins++;
        }
        else if ((cents < 5) && (cents >= 1))
        {
            cents = cents - 1;
            coins++;
        }
    }

    //prints the number of coins needed.
    printf("%i\n", coins);
}