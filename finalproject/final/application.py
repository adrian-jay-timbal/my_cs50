import os
import csv

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///storage.db")


@app.route("/")
@login_required
def index():
    """Show dashboard"""

    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    name = db.execute("SELECT firstname FROM profiles WHERE user_id = :user_id",
                      user_id=session["user_id"])
    assessments = db.execute("SELECT * FROM assessments WHERE user_id = :user_id",
                              user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])
    house_count = db.execute("SELECT * FROM profiles WHERE house = :house",
                             house=profiles[0]["house"])

    l_stat = ""
    if user[0]["level"] <= 10:
        l_stat = "Beginner"
    elif user[0]["level"] >= 11 and user[0]["level"] <= 20:
        l_stat = "Advance"
    elif user[0]["level"] >= 21 and user[0]["level"] <= 30:
        l_stat = "Intelligent"
    elif user[0]["level"] >= 31:
        l_stat = "Legend"

    if user[0]["position"] == "teacher":
        messages = db.execute("SELECT * FROM reminders WHERE user_id = :user_id ORDER BY time DESC LIMIT 1",
                              user_id=session["user_id"])

        new_student = db.execute("SELECT * FROM profiles WHERE user_id IN (SELECT user_id FROM myteacher WHERE teacher = :teacher) ORDER BY user_id DESC LIMIT 3",
                                 teacher=user[0]["username"])
        students = db.execute("SELECT user_id FROM myteacher WHERE teacher = :teacher",
                              teacher=user[0]["username"])
        points = db.execute("SELECT level FROM users WHERE id IN (SELECT user_id FROM myteacher WHERE teacher = :teacher)",
                            teacher=user[0]["username"])

        point_count = 0
        for p in points:
            point_count += p['level']

        if len(students) != 0:
            f_count = point_count // len(students)
        else:
            f_count = 0

        teachers = db.execute("SELECT house, firstname FROM profiles WHERE user_id IN (SELECT id FROM users WHERE position = 'teacher') ORDER BY firstname LIMIT 10")

        return render_template("teacher_index.html",
                               m_count=len(messages), a_count=len(assessments),
                               f_count=f_count, students=len(students),
                               profiles=profiles, house_count=len(house_count),
                               teachers=teachers, new_student=new_student, user=user, reminder=messages)
    else:
        s_reminders = db.execute("SELECT * FROM reminders WHERE user_id = "
                                 "(SELECT id from users WHERE username = "
                                 "(SELECT teacher FROM myteacher WHERE user_id = :user_id)) ORDER BY time DESC LIMIT 1",
                                 user_id=session["user_id"])

        teacher = db.execute("SELECT firstname FROM profiles WHERE user_id = "
                             "(SELECT id from users WHERE username = "
                             "(SELECT teacher FROM myteacher WHERE user_id = :user_id))",
                             user_id=session["user_id"])

        classmates = db.execute("SELECT house, firstname FROM profiles WHERE user_id IN "
                                "(SELECT user_id FROM myteacher WHERE teacher = "
                                "(SELECT username FROM users WHERE id = "
                                "(SELECT id from users WHERE username = "
                                "(SELECT teacher FROM myteacher WHERE user_id = :user_id)))) ORDER BY firstname LIMIT 10",
                                user_id=session["user_id"])
        reports = db.execute("SELECT * FROM myreport WHERE user_id = :user",
                             user=session["user_id"])

        return render_template("student_index.html",
                               m_count=len(s_reminders), a_count=len(reports), house_count=len(house_count),
                               f_count=user[0]["level"], l_stat=l_stat, teacher=teacher[0]["firstname"],
                               classmates=classmates, assessments=reports, profiles=profiles, user=user, reminder=s_reminders)


@app.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])
    assessments = db.execute("SELECT * FROM assessments WHERE user_id = :user_id",
                             user_id=session["user_id"])

    if user[0]["position"] == "teacher":

        db.execute("DELETE FROM temp WHERE user_id = :user",
                   user=session["user_id"])

        if len(assessments) != 0:
            last_ass = db.execute("SELECT number FROM assessments WHERE user_id = :user_id ORDER BY number DESC LIMIT 1",
                                  user_id=session["user_id"])
            number = last_ass[0]["number"] + 1
        else:
            number = 1

        if request.method == "POST":
            title = request.form.get("title")
            qnumber = request.form.get("qnumber")
            subject = request.form.get("subject")
            qtype = request.form.get("type")

            db.execute("INSERT INTO assessments ('user_id', 'number', 'title', 'subject', 'type', 'length') VALUES (:user_id, :number, :title, :subject, :qtype, :length)",
                       user_id=session["user_id"], number=number, title=title, subject=subject, qtype=qtype, length=qnumber)

            return redirect("/assessment")
        else:
            return render_template("teacher_ass.html", user=user, profiles=profiles,
                                   assessments=assessments, number=number)
    else:

        teacher = db.execute("SELECT teacher FROM myteacher WHERE user_id = :user_id",
                             user_id=session["user_id"])

        active_teacher = db.execute("SELECT id FROM users WHERE username = :user",
                                    user=teacher[0]["teacher"])

        active = db.execute("SELECT * FROM active WHERE user_id = :user_id",
                            user_id=active_teacher[0]["id"])

        reports = db.execute("SELECT * FROM myreport WHERE user_id = :user",
                             user=session["user_id"])

        return render_template("student_ass.html", active=active, myreport=reports,
                               user=user, profiles=profiles, len_active=len(active))


@app.route("/questions", methods=["GET", "POST"])
@login_required
def questions():

    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])

    if request.method == "POST":
        if request.form.get("ass_id") != None:
            ass_id = request.form.get("ass_id")

            db.execute("INSERT INTO temp ('id', 'user_id') VALUES (:ass_id, :user_id)",
                       ass_id=ass_id, user_id=session["user_id"])

            new_id = db.execute("SELECT * FROM temp WHERE user_id = :user",
                                user=session["user_id"])

            assessments = db.execute("SELECT * FROM assessments WHERE id = :ass_id",
                                     ass_id=new_id[0]["id"])
            questions = db.execute("SELECT * FROM questions WHERE ass_id = :ass_id",
                                   ass_id=new_id[0]["id"])
            number = len(questions) + 1

            return render_template("questions.html", user=user, profiles=profiles,
                                   assessments=assessments, number=number, questions=questions)
        else:
            new_id = db.execute("SELECT * FROM temp WHERE user_id = :user",
                                user=session["user_id"])

            assessments = db.execute("SELECT * FROM assessments WHERE id = :ass_id",
                                     ass_id=new_id[0]["id"])
            questions = db.execute("SELECT * FROM questions WHERE ass_id = :ass_id",
                                   ass_id=new_id[0]["id"])
            number = len(questions) + 1

            question = request.form.get("question")
            option_a = request.form.get("option_a")
            option_b = request.form.get("option_b")
            option_c = request.form.get("option_c")
            option_d = request.form.get("option_d")
            answer = request.form.get("answer")

            db.execute("INSERT INTO questions ('ass_id', 'question', 'answer', 'number') VALUES (:ass_id, :question, :answer, :number)",
                       ass_id=new_id[0]["id"], question=question, answer=answer, number=number)

            if assessments[0]["type"] == "choices":
                q_id = db.execute("SELECT id FROM questions WHERE ass_id = :ass_id AND number = :number",
                                  ass_id=new_id[0]["id"], number=number)

                db.execute("INSERT INTO options ('question_id', 'a', 'b', 'c', 'd', 'ass_id') VALUES (:q_id, :option_a, :option_b, :option_c, :option_d, :ass_id)",
                           q_id=q_id[0]["id"], option_a=option_a, option_b=option_b, option_c=option_c, option_d=option_d, ass_id=new_id[0]["id"])

            return redirect("/questions")

    else:
        new_id = db.execute("SELECT * FROM temp WHERE user_id = :user",
                            user=session["user_id"])

        assessments = db.execute("SELECT * FROM assessments WHERE id = :ass_id",
                                 ass_id=new_id[0]["id"])
        questions = db.execute("SELECT * FROM questions WHERE ass_id = :ass_id",
                               ass_id=new_id[0]["id"])
        number = len(questions) + 1

        return render_template("questions.html", user=user, profiles=profiles,
                               assessments=assessments, number=number, questions=questions)


@app.route("/deploy", methods=["GET", "POST"])
@login_required
def deploy():

    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])
    assessments = db.execute("SELECT * FROM assessments WHERE user_id = :user_id",
                             user_id=session["user_id"])
    new_id = db.execute("SELECT * FROM temp WHERE user_id = :user",
                        user=session["user_id"])

    if request.method == "POST":
        act_id = request.form.get("id")
        qnumber = request.form.get("number")
        title = request.form.get("title")
        subject = request.form.get("subject")
        qtype = request.form.get("type")
        inumber = request.form.get("length")

        db.execute("INSERT INTO temp ('id', 'user_id') VALUES (:ass_id, :user_id)",
                   ass_id=act_id, user_id=session["user_id"])

        db.execute("INSERT INTO active ('id', 'user_id', 'number', 'title', 'subject', 'type', 'length') VALUES (:act_id, :user_id, :number, :title, :subject, :qtype, :length)",
                   act_id=act_id, user_id=session["user_id"], number=qnumber, title=title, subject=subject, qtype=qtype, length=inumber)

        return redirect("/deploy")

    else:
        if len(new_id) != 1:
            active = [{'id': 0}]
            len_act = len(active) - 1
        else:
            active = db.execute("SELECT * FROM active WHERE id = :act_id",
                                act_id=new_id[0]["id"])
            len_act = len(active)

        return render_template("deploy.html", user=user, profiles=profiles,
                               assessments=assessments, active=active,
                               len_act=len_act)


@app.route("/d_questions", methods=["GET", "POST"])
@login_required
def d_questions():
    if request.method == "POST":

        ass_id = request.form.get("ass_id")

        db.execute("DELETE FROM questions WHERE ass_id = :ass_id",
                   ass_id=ass_id)

        return redirect("/questions")


@app.route("/terminate", methods=["GET", "POST"])
@login_required
def terminate():
    if request.method == "POST":

        act_id = request.form.get("id")

        db.execute("DELETE FROM active WHERE id = :act_id",
                   act_id=act_id)
        db.execute("DELETE FROM temp WHERE id = :act_id",
                   act_id=act_id)

        return redirect("/deploy")


@app.route("/take", methods=["GET", "POST"])
@login_required
def take():
    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])
    teacher = db.execute("SELECT teacher FROM myteacher WHERE user_id = :user_id",
                         user_id=session["user_id"])
    active_teacher = db.execute("SELECT id FROM users WHERE username = :user",
                                user=teacher[0]["teacher"])
    active = db.execute("SELECT * FROM active WHERE user_id = :user_id",
                        user_id=active_teacher[0]["id"])

    # if the teacher acidentally stoped the assessment while student still take exam
    # they will be redirected to the offline assessment page
    if len(active) == 0:
        return redirect("/assessment")

    questions = db.execute("SELECT * FROM questions WHERE ass_id = :active",
                           active=active[0]["id"])
    options = db.execute("SELECT * FROM options WHERE ass_id = :ass_id",
                         ass_id=active[0]["id"])

    if request.method == "POST":
        score = 0

        # check answers
        # compare if the current number answer
        # is equal to current index answer
        for i in range(len(questions)):
            if request.form.get(str(i + 1)) == questions[i]["answer"]:
                score += 1

        end = datetime.now()
        dt = end.strftime("%d/%m/%Y %H:%M:%S")

        db.execute("INSERT INTO reports ('name', 'ass_id', 'ass_name', 'score', 'time', 'user_id') VALUES (:name, :ass_id, :ass_name, :score, :time, :user)",
                   name=f"{profiles[0]['firstname']} {profiles[0]['lastname']}", ass_id=active[0]["id"],
                   ass_name=active[0]["title"], score=score, time=dt, user=active_teacher[0]["id"])
        db.execute("INSERT INTO myreport ('user_id', 'ass_name', 'score', 'time') VALUES (:user, :ass_name, :score, :time)",
                   user=session["user_id"], ass_name=active[0]["title"], score=score, time=dt)

        points = user[0]["level"] + score

        db.execute("UPDATE users SET level = :level WHERE id = :user_id",
                   level=points, user_id=session["user_id"])

        return redirect("/report")

    else:

        return render_template("take.html", active=active, questions=questions,
                               user=user, profiles=profiles, options=options,
                               q_len=len(questions))


@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])
    teacher = db.execute("SELECT teacher FROM myteacher WHERE user_id = :user_id",
                         user_id=session["user_id"])

    if user[0]["position"] == "teacher":

        if request.method == "POST":

            ass_id = request.form.get("id")

            reports = db.execute("SELECT * FROM reports WHERE user_id = :user AND ass_id = :ass ORDER BY score",
                                 user=session["user_id"], ass=ass_id)
            if len(reports) != 0:
                return render_template("details.html", reports=reports,
                                       user=user, profiles=profiles)
            else:
                return apology("You don't have report to view from this exam.")

        else:
            reports = db.execute("SELECT * FROM assessments WHERE user_id = :user",
                                 user=session["user_id"])

            return render_template("report.html", reports=reports,
                                   user=user, profiles=profiles)
    else:
        reports = db.execute("SELECT * FROM myreport WHERE user_id = :user",
                             user=session["user_id"])
        return render_template("report.html", reports=reports,
                               user=user, profiles=profiles)


@app.route("/export", methods=["GET", "POST"])
@login_required
def export():
    if request.method == "POST":
        ass_id = request.form.get("id")

        reports = db.execute("SELECT * FROM reports WHERE user_id = :user AND ass_id = :ass ORDER BY score",
                             user=session["user_id"], ass=ass_id)

        if len(reports) != 0:

            db.execute("DELETE FROM d_temp WHERE ass_id = :ass_id",
                       ass_id=ass_id)

            if os.path.exists("downloads/"+reports[0]["ass_name"]+".csv"):
                os.remove("downloads/"+reports[0]["ass_name"]+".csv")

            db.execute("INSERT INTO d_temp ('ass_id', 'user_id', title) VALUES (:ass_id, :user_id, :title)",
                       ass_id=ass_id, user_id=session["user_id"], title=reports[0]["ass_name"])

            with open("downloads/"+reports[0]["ass_name"]+".csv", "w") as file:
                fieldnames = ['name', 'ass_name', 'score', 'time']

                csv_writer = csv.DictWriter(file, fieldnames=fieldnames)

                csv_writer.writeheader()

                for report in reports:
                    del report['user_id']
                    del report['ass_id']
                    csv_writer.writerow(report)

            return redirect("/export")

        else:

            return apology("You don't have report to download from this exam.")
    else:

        d_name = db.execute("SELECT title FROM d_temp WHERE user_id = :user",
                          user=session["user_id"])

        d_file = f"{d_name[0]['title']}.csv"

        return send_file("downloads/"+d_file, as_attachment=True)


@app.route("/reminder", methods=["GET", "POST"])
@login_required
def reminder():

    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])
    reminders = db.execute("SELECT * FROM reminders WHERE user_id = :user_id ORDER BY time DESC",
                           user_id=session["user_id"])

    end = datetime.now()
    timen = end.strftime("%m-%d-%Y %H:%M:%S")

    if request.method == "POST":

        message = request.form.get("message")

        db.execute("INSERT INTO reminders ('user_id', 'reminder', 'time') VALUES (:user_id, :remind, :timen)",
                   user_id=session["user_id"], remind=message, timen=timen)

        return redirect("/reminder")
    else:

        if user[0]["position"] == "teacher":
            return render_template("reminders.html", user=user, profiles=profiles,
                                   reminders=reminders, today=timen)
        else:
            s_reminders = db.execute("SELECT * FROM reminders WHERE user_id = "
                                     "(SELECT id from users WHERE username = "
                                     "(SELECT teacher FROM myteacher WHERE user_id = :user_id)) ORDER BY time DESC",
                                     user_id=session["user_id"])

            return render_template("reminders.html", user=user, profiles=profiles,
                                   reminders=s_reminders, today=timen)


@app.route("/d_reminders", methods=["GET", "POST"])
@login_required
def d_reminders():

    db.execute("DELETE FROM reminders WHERE user_id = :user_id",
               user_id=session["user_id"])

    return redirect("/reminder")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # setting variables
    new_user = request.form.get("username")
    new_email = request.form.get("email")
    new_password = request.form.get("password")
    new_position = request.form.get("position")
    new_confirmation = request.form.get("confirmation")

    # check request method
    if request.method == "POST":

        # Ensure username was submitted
        if not new_user.isalpha():
            return apology("must provide proper username")

        # Ensure password confirmation
        elif new_password != new_confirmation:
            return apology("must confirm you password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=new_user)

        # Ensure username uniqueness
        if len(rows) == 1:
            return apology("username already exist")

        # used hash function to generate hash value of the password
        new_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)

        # add data to database
        db.execute("INSERT INTO users ('username', 'hash', 'email', 'position') VALUES (:username, :my_hash, :email, :position)",
                                       username=new_user, my_hash=new_hash, email=new_email, position=new_position)

        # Query database for id
        row = db.execute("SELECT * FROM users WHERE username = :username",
                          username=new_user)

        # Remember which user has logged in
        session["user_id"] = row[0]["id"]

        if new_position != "teacher":
            return redirect("/register1")
        else:
            return redirect("/register2")

    else:
        return render_template("register.html")


@app.route("/register1", methods=["GET", "POST"])
def register1():
    """Register user"""
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    myteacher = request.form.get("myteacher")
    myhouse = request.form.get("myhouse")
    gender = request.form.get("gender")

    if request.method == "POST":

        db.execute("INSERT INTO profiles ('user_id', 'firstname', 'lastname', 'house', 'gender') VALUES (:user_id, :firstname, :lastname, :house, :gender)",
                   user_id=session["user_id"], firstname=firstname, lastname=lastname, house=myhouse, gender=gender)
        db.execute("INSERT INTO myteacher ('user_id', 'teacher') VALUES (:user_id, :teacher)",
                   user_id=session["user_id"], teacher=myteacher)

        # Redirect user to confirmation
        return redirect("/")
    else:

        teachers = db.execute("SELECT username FROM users WHERE position = 'teacher'")
        return render_template("register1.html", teachers=teachers)


@app.route("/register2", methods=["GET", "POST"])
def register2():
    """Register user"""
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    myhouse = request.form.get("myhouse")
    gender = request.form.get("gender")

    if request.method == "POST":

        db.execute("INSERT INTO profiles ('user_id', 'firstname', 'lastname', 'house', 'gender') VALUES (:user_id, :firstname, :lastname, :house, :gender)",
                   user_id=session["user_id"], firstname=firstname, lastname=lastname, house=myhouse, gender=gender)


        return redirect("/")
    else:

        return render_template("register2.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])

    if request.method == "POST":
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        age = request.form.get("age")
        major = request.form.get("major")
        school = request.form.get("school")
        sayings = request.form.get("sayings")

        db.execute("UPDATE profiles SET firstname = :fname, lastname = :lname,"
                   "major = :major, school = :school, sayings = :sayings, age = :age "
                   "WHERE user_id = :user", fname=fname, lname=lname, age=age,
                   major=major, school=school, sayings=sayings, user=session["user_id"])

        return redirect("/")
    else:
        return render_template("settings.html", user=user, profiles=profiles)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():

    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])

    # set variables from inputs
    old_pass = request.form.get("old_password")
    new_pass = request.form.get("new_password")
    confirm = request.form.get("confirmation_new")

    # check request method
    if request.method == "POST":

        # Ensure old password was submitted
        if not old_pass:
            return apology("must provide your current password")

        # Ensure password was submitted
        elif not new_pass:
            return apology("must provide new password")

        # Ensure password confirmation
        elif new_pass != confirm:
            return apology("must confirm you password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=session["user_id"])

        # check if old and new password matched
        if check_password_hash(rows[0]["hash"], old_pass):

            if new_pass == confirm:

                # set hash value for new password
                new_hash = generate_password_hash(new_pass, method='pbkdf2:sha256', salt_length=8)

                # update database for new password
                db.execute("UPDATE users SET hash = :my_hash WHERE username = :username",
                           username=rows[0]["username"], my_hash=new_hash)

                return render_template("confirm.html", message="Change Password Successful")
            else:
                return apology("sorry, password confirmation failed")
        else:
            return apology("sorry, incorrect current password")
    else:
        return render_template("password.html", profiles=profiles, user=user)


@app.route("/student_list", methods=["GET", "POST"])
@login_required
def student_list():

    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])

    if user[0]["position"] == "teacher":
        students = db.execute("SELECT * FROM profiles WHERE user_id IN (SELECT user_id FROM myteacher WHERE teacher = :teacher) ORDER BY lastname",
                              teacher=user[0]["username"])
    else:
        students = db.execute("SELECT * FROM profiles WHERE user_id IN "
                              "(SELECT user_id FROM myteacher WHERE teacher = "
                              "(SELECT username FROM users WHERE id = "
                              "(SELECT id from users WHERE username = "
                              "(SELECT teacher FROM myteacher WHERE user_id = :user_id)))) ORDER BY firstname LIMIT 10",
                              user_id=session["user_id"])

    return render_template("students.html", user=user, profiles=profiles,
                           students=students)


@app.route("/find", methods=["GET", "POST"])
@login_required
def find():
    user = db.execute("SELECT * FROM users WHERE id = :user_id",
                      user_id=session["user_id"])
    profiles = db.execute("SELECT * FROM profiles WHERE user_id = :user_id",
                          user_id=session["user_id"])

    if request.method == "POST":
        person = request.form.get("search")

        results = db.execute("SELECT * FROM profiles WHERE firstname LIKE :search",
                             search="%"+person+"%")

        return render_template("find.html", user=user, profiles=profiles, results=results)

    else:
        person = ""

        results = db.execute("SELECT * FROM profiles WHERE firstname LIKE :search",
                             search=person)

        return render_template("find.html", user=user, profiles=profiles, results=results)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

