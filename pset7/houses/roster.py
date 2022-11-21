# libraries
from cs50 import SQL
from sys import argv

# create connection to the database
db = SQL("sqlite:///students.db")

# check for valid arguments
argc = len(argv)
if argc != 2:
    print("Error: Invalid argument")
else:
    # query from the database
    results = db.execute("SELECT * FROM students WHERE house = ? ORDER BY last", argv[1])

    # itirate through the results and assign it to variables
    for result in results:
        f_name = result["first"]
        m_name = result["middle"]
        l_name = result["last"]
        birthyear = result["birth"]

        # check if middle name is not null
        if m_name != None:
            name = f"{f_name} {m_name} {l_name}"
        else:
            name = f"{f_name} {l_name}"

        # print each names and birthyear as results
        print(f"{name}, born {birthyear}")
