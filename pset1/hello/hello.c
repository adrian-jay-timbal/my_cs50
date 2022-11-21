/*import module*/
#include <unistd.h>
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    /*Getting inputs from the user*/
    string name = get_string("Hi there, what is your name?\n: ");

    /*Prints the message Hello, 'name' wait 1s and prints Welcome to CS50 on screen*/
    printf("Hello, %s\n", name);
    sleep(1);
    printf("Welcome to CS50!\n");
}