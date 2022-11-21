// Implements a dictionary's functionality

#include <stdbool.h>
#include <string.h>
#include <strings.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
const unsigned int N = 500000;

// Hash table
node *table[N];

int word_count = 0;

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    //accessing the table using the hashed value of word given
    int index = hash(word);
    for (node *i = table[index]; i != NULL; i = i->next)
    {
        //compare if word is in the dictionary
        //disregarding cases
        if (strcasecmp(word, i->word) == 0)
        {
            //return true if found
            return true;
        }
    }
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    int add = 0;
    int mul = 1;
    for (int i = 0; i < strlen(word); i++)
    {
        //operate each character value
        add += tolower(word[i]) * mul;
        add -= 'a';
        mul++;
    }

    //return the sum of the added value to be the hash value
    return (add);
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    //open dictionary file
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        return false;
    }

    char temp[LENGTH + 1];
    while (fscanf(file, "%s", temp) != EOF)
    {
        //create new node to store the scanned word from the file
        node *new_node = malloc(sizeof(node));
        if (new_node == NULL)
        {
            return false;
        }
        strcpy(new_node->word, temp);
        new_node->next = NULL;

        //placing the pointers on the right direction
        int i = hash(temp);
        if (table[i] == NULL)
        {
            //add word if the table is empty
            table[i] = new_node;
        }
        else
        {
            //add word if the table is not empty
            new_node->next = table[i];
            table[i] = new_node;
        }

        //increment the number of words added to the list
        word_count++;
    }
    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    //return the number of words added to the table
    return word_count;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    //itirates through the hash table
    for (int current = 0; current < N; current++)
    {
        //initialize pointers to the first element in the linked list
        node *list = table[current];
        node *step = list;
        node *back = list;

        //itirates through the linked list on that indexed table
        //free the used space
        while (step != NULL)
        {
            step = step->next;
            free(back);
            back = step;
        }
    }
    return true;
}
