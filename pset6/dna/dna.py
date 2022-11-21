from sys import argv
import csv


def counter(file, dna_name):
    answer = 0
    end_word = len(dna_name)
    end_file = len(file)

    # itirates on every characters on the text file
    for items in range(end_file):
        count = 0
        while True:
            i = items + end_word * count
            j = i + end_word
            # check to if match is found to add the count of consecutive dna name
            if file[i:j] == dna_name:
                count += 1
            else:
                break
        # check who has the higher value between answer and count to be the new answer value
        answer = max(answer, count)
    return answer


#argv = sys.argv
argc = len(argv)

if argc != 3:
    print("Usage: python dna.py data.csv sequence.txt")
else:
    # open the csv file in read mode as a dictionary
    with open(argv[1], "r") as csv_file:
        csv_read = csv.DictReader(csv_file)

        # open text file
        with open(argv[2], "r") as text_file:
            text_read = text_file.read()

        # temporary data structure to hold values
        holder = {}

        # iterates through the fieldnames on the csv file
        # assign the value to the holder variable
        for STR in csv_read.fieldnames[1:]:
            holder[STR] = counter(text_read, STR)
            #print(STR, counter(text_read, STR))

        # prints the name of the person with matching dna from the csv data with the holder variable
        # and prints no match instead
        for row in csv_read:
            if all(holder[key] == int(row[key]) for key in holder):
                print(row["name"])
                exit()
        print("No match")

