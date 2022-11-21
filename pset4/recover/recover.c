#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main(int argc, char *argv[])
{
    //getting valid argument from the user
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }
    //open the raw file
    FILE *card = fopen(argv[1], "r");

    //file check if it opened
    if (card == NULL)
    {
        //if it can't open, print this
        printf("failed to open file\n");
        return 1;
    }

    //definition of new type unsigned int from stdint.h
    typedef uint8_t BYTE;

    //variables used
    int end = 0;
    BYTE temp[512];
    int count;
    int jpeg_count = 0;
    FILE *file;
    char newfile[50];
    int file_count = 0;

    while (end == 0)
    {
        //read the raw file in 512 bytes chunk and put it in a buffer
        count = fread(temp, sizeof(BYTE), 512, card);
        if (count == 0)
        {
            end++;
        }

        //check for the header of a jpeg file
        if ((temp[0] == 0xff) && (temp[1] == 0xd8) && (temp[2] == 0xff) && ((temp[3] & 0xf0) == 0xe0))
        {
            //check if it is the first jpeg header found
            if (jpeg_count == 0)
            {
                jpeg_count++;
            }
            else
            {
                //close the previous file if new jpeg header was found
                fclose(file);
            }

            //create a new jpeg file everytime it founds a jpeg header
            sprintf(newfile, "%03i.jpg", file_count);
            file = fopen(newfile, "w");
            fwrite(temp, sizeof(BYTE), count, file);
            file_count++;
        }
        else
        {
            //if already writing bytes on a file
            //continue writing 512 bytes on that file
            //if no jpeg header was found on the current block of 512 bytes
            if (jpeg_count > 0)
            {
                fwrite(temp, sizeof(BYTE), count, file);
            }
        }
    }

    //close all previously opened file
    fclose(card);
    fclose(file);
    return 0;
}