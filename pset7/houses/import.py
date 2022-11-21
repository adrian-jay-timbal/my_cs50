# libraries
from cs50 import SQL
from sys import argv
import csv

# create connection to the database
db = SQL("sqlite:///students.db")

# calculate the length of arguments
argc = len(argv)

# error checking for invalid argumetns
if argc != 2:
    print("Error: Invalid arguments")
else:
    # open and read the csv file
    with open(argv[1], "r") as csv_file:
        csv_open = csv.DictReader(csv_file)

        # iterate through the rows of csv file
        for row in csv_open:
            birth = int(row["birth"])

            # split names by spaces
            name = row["name"].split()

            # check for middle name
            # and assign it to a variable
            if len(name) == 3:
                middle = name[1]
                last = name[2]
            else:
                middle = None
                last = name[1]
            first = name[0]

            house = row["house"]

            # inserting data to database based on the generated value from csv file above
            db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES(?, ?, ?, ?, ?)",
                       first, middle, last, house, birth)

