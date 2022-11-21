# Project ZONE description

This is a website that is mainly to conduct assessments and produce automated reports.
The inspiration for this project is to help teachers on conducting assessments where they will no longer manually check assessments and create reports.
This also help the student more computer friendly, by exposing students to use computers as their main equipment for their activities and assessments.

This web has 6 main pages after login or registration, namely:
* Home
* Reminders
* Assessments
* Students/Classmates
* Find
* Settings

#### This web has two types of users, students and teachers.

### All users

1. Home - after login or registration, users will be redirected to / route on the web application
          which will render the homepage. Homepage displays general information such as user profile information, thier chosen
          team (just for fun), co-teachers for teachers and classmates for students, recently enrolled student, references and the footer.
2. Find - the application take input via form and query the database for all users firstname base on the keyword given by the user.
          It displays all the informations found for that keyword.
3. Settings - the user has the authority to change something on their profile and they also have an option to change their password.

### Teacher-side

1. Reminders - /reminder route, the application allows the user to post notifications and reminders that only their
               students can see. Teachers will see all the reminders they posted tagged with date and time for each
               post. Teachers also have the authority to clear all thier post when its no longer relevant. All actions
               here are performed by the application by querying the database.
2. Assessments - this have 3 parts:
    * Create - create assessment page shows the teacher all of the assessments
               they created in table form with buttton to edit the questions on the assessment of their choice.
               There is also a form which allow teachers to create new assessment to be stored in the database
               via /assessment route. During the creation process, user will be taken to /question route that
               allows the user to add questions with the options and answer to the assessment they created.
    * Deploy - the application allows the user to activate and deactivate the assessment of their choice to be available for their
               students to take the assessment. The limitation is that only one assessment is allowed to be active at a time.
    * Report - report page displays the list of their assessments and has two button to choose what action they want.
               Details  button, the application allows the user to view the detailed report of the student performance on that
               assessment. The download button on the other hand allows the user to download the report on a csv file format.
3. Students - the application will display all of the students registered on the teacher.

### Student-side

1. Reminders - for students, this only displays post from their teacher.
2. Assessments - this page displays user all previous assessments they take. If an assessment is active, this displays
                 a card that has form to take the assessment and will be taken to the /take route that allows the user
                 to take the assessment on a certain period of time base on how questions there are. If the student
                 failed to finish the assessment on given time period that is shown on the upper left part of the page
                 it will hide all html element exept for a button to submit thier current answers. After submitting,
                 user are redirected to the /report route that displays the summary and result of their assessment. The
                 application automaticatilly check for correct answers and count the number of scores.
3. Students - the application will display all of the students registered on the teacher.

### Special thanks to:

* w3school as I take advantage of their css library, this project is powered by w3 css.
* bootstrap, I also use some bootstrap css on login and registration pages.
* fontawesome ass my main source of icons
* flaticon for some other icons

### The application

The application is written in python language and built with python flask, werkzeug and jinja to operate this website.
The application also use some other python library such as:
* os to access local files
* SQL from cs50 library used as main connection and execute queries between the application and the database.
* csv library to create downloadable csv file
* datetime to generate current date and time