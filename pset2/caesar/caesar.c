//libraries needed
#include <cs50.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>

//funtion prototype
void caesar(int num, string pt);

//main program
int main(int argc, string argv[])
{
    //checking the argument
    if (argc != 2)
    {
        printf("missing arguments: KEY\n");
        return 1;
    }

    for (int i = 0; i < strlen(argv[1]); i++)
    {
        if (!isdigit(argv[1][i]))
        {
            printf("key must be an integer\n");
            return 1;
        }
    }

    int key = atoi(argv[1]);

    if (key > 0)
    {
        //getting the plaintext input
        string text = get_string("plaintext: ");
        caesar(key, text);
        return 0;
    }
    else
    {
        printf("key must be a non negative integer\n");
        return 1;
    }
}

//function for encrypting the plaintext
void caesar(int num, string pt)
{
    printf("ciphertext: ");
    for (int i = 0; i <= strlen(pt); i++)
    {
        if (isupper(pt[i]))
        {
            pt[i] = toupper(((pt[i] - 'A') + num) % 26 + 'A');
        }
        if (islower(pt[i]))
        {
            pt[i] = tolower(((pt[i] - 'a') + num) % 26 + 'a');
        }
    }
    printf("%s\n", pt);
}