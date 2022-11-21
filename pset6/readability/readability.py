# import get_string from cs50 library
from cs50 import get_string

# variables used
let = 0
sen = 0
wor = 1

# get text input from the user
text = get_string("Text: ")

# count the value of each variable above
for i in range(len(text)):
    if text[i].isalpha():
        let += 1
    elif text[i] == " ":
        wor += 1
    elif text[i] == "." or text[i] == "!" or text[i] == "?":
        sen += 1

# coleman-liau computations
l = (100 / wor) * let
s = (100 / wor) * sen
index = 0.0588 * l - 0.296 * s - 15.8
final = round(index)

# print grade level based on the computation
if final > 16:
    print("Grade 16+")
elif final < 1:
    print("Before Grade 1")
else:
    print("Grade", final)