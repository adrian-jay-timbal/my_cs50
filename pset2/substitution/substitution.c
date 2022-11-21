//libraries used
#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

//function prototype
bool validity(string text);

//main program
int main(int argc, string argv[])
{
    string argument = argv[1];
    if (argc != 2)
    {
        printf("invalid command-line argument\n");
        return 1;
    }
    else
    {
        if (!validity(argument))
        {
            return 1;
        }

        //get the input as plaintext and prints the ciphertext
        string pt = get_string("plaintext: ");
        //iterate through the characters of the input
        //and replace it with the character on the argument variable above.
        for (int i = 0; i <= strlen(pt); i++)
        {
            if (islower(pt[i]))
            {
                pt[i] = tolower(argument[pt[i] - 'a']);
            }
            if (isupper(pt[i]))
            {
                pt[i] = toupper(argument[pt[i] - 'A']);
            }
        }
        printf("ciphertext: %s\n", pt);
        return 0;
    }
}

//boolian function that is used to check the validity of the key
//used as if statement on line 21.
bool validity(string text)
{
    int n = strlen(text);
    if (n != 26)
    {
        printf("argument must contain 26 characters\n");
        return false;
    }
    else
    {
        int freq[26] = { 0 };
        for (int i = 0; i < n; i++)
        {
            if (!isalpha(text[i]))
            {
                printf("argument must not contain special characters\n");
                return false;
            }

            int index = toupper(text[i]) - 'A';
            if (freq[index] > 0)
            {
                printf("The key should not have duplicate characters\n");
                return false;
            }

            freq[index]++;
        }

        return true;
    }
}