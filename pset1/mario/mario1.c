//adds the required library
#include <cs50.h>
#include <stdio.h>
//prototyping functions
void mario(void);

//execution of the main programm
int main(void)
{
    mario();
    return 0;
}

//function for building the blocks
void mario(void)
{
    int n, r, c;
    do
    {
        //prompt user input
        n = get_int("Enter the height: ");
    }
    while (n < 1 || n > 8);

    //prints the blocks according to user input
    for (r = 1; r <= n; r++)
    {
        for (c = 1; c <= n; c++)
        {
            if (c >= n - (r - 1))
            {
                printf("#");
            }
            else
            {
                printf(" ");
            }
        }
        printf("\n");
    }
}
