//libraries needed
#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <math.h>

//prototype
void user_input(void);
void coleman(void);

//main variables used
int Let = 0, Sen = 0, Wor = 0 + 1, findex;

//main program execution
int main(void)
{
    user_input();
    coleman();
}

//get the user input which is the text and identifies it
//to add values to the main variables
void user_input(void)
{
    string text = get_string("Text: ");

    for (int i = 0, n = strlen(text); i < n; i++)
    {
        if (text[i] >= 'A' && text[i] <= 'z')
        {
            Let++;
        }
        else if (text[i] == ' ')
        {
            Wor++;
        }
        else if ((text[i] == '.') || (text[i] == '!') || (text[i] == '?'))
        {
            Sen++;
        }
    }
}

//the coleman-liau computations
void coleman(void)
{
    float L, S, index;

    L = ((float)100 / Wor) * Let;
    S = ((float)100 / Wor) * Sen;
    index = 0.0588 * L - 0.296 * S - 15.8;
    findex = round(index);

    if (findex > 16)
    {
        printf("Grade 16+\n");
    }
    else if (findex < 1)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade %i\n", findex);
    }
}