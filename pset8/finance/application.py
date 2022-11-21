import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# added library
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


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # query data from database
    current_money = db.execute("SELECT cash FROM users WHERE id = :current_user",
                               current_user=session["user_id"])
    last_reports = db.execute("SELECT * FROM purchase WHERE user_id = :current_user GROUP BY stock",
                              current_user=session["user_id"])

    # check users owned stocks
    for report in last_reports:
        if int(report["share"]) == 0:
            db.execute("DELETE FROM purchase WHERE stock = :current_stock", current_stock=report["stock"])

    reports = db.execute("SELECT * FROM purchase WHERE user_id = :current_user GROUP BY stock",
                         current_user=session["user_id"])

    # iterates through generated report from the database
    # used as output on index.html page
    new_cash = 0
    for report in reports:
        prices = lookup(report["stock"])
        report["cost"] = "{:,.2f}".format(float(prices["price"]))
        report["total"] = float(prices["price"]) * int(report["share"])
        new_cash += float(report["total"])
        report["total"] = "{:,.2f}".format(float(report["cost"]) * int(report["share"]))

    balance = float(current_money[0]["cash"])
    total_cash = "{:,.2f}".format(float(new_cash + float(balance)))
    balance = "{:,.2f}".format(balance)

    # render index.html page
    return render_template("index.html", reports=reports, balance=balance, total_cash=total_cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # check request method used
    if request.method == "POST":
        quoted_value = lookup(request.form.get("symbol"))
        share_value = request.form.get("shares")

        # check input values to validate
        if quoted_value == None:
            return apology("provide valid symbol", 403)
        elif share_value == "" or int(share_value) <= 0:
            return apology("must provide the number of shares", 403)

        # query data from database using cs50 library SQL
        duplicates = db.execute("SELECT * FROM purchase WHERE name = :current AND user_id = :user_id",
                                current=quoted_value["name"], user_id=session["user_id"])
        current_money = db.execute("SELECT cash FROM users WHERE id = :current_user",
                                   current_user=session["user_id"])

        # check if user already own the requested stock
        if len(duplicates) == 1:

            # check if user have enough cash to purchase
            if current_money[0]["cash"] >= quoted_value["price"]:

                # set the new value of shares
                new_share = int(duplicates[0]["share"]) + int(share_value)

                # update database with the new value of shares
                db.execute("UPDATE purchase SET share = :new_share WHERE name = :name",
                           new_share=new_share, name=quoted_value["name"])

                # set the new value of users cash
                balance = round(current_money[0]["cash"] - (float(quoted_value["price"]) * int(share_value)), 2)

                # update the database of users cash
                db.execute("UPDATE users SET cash = :balance WHERE id = :current_user",
                           balance=balance, current_user=session["user_id"])

                # add transactions to users history
                now = datetime.now()
                dt = now.strftime("%d/%m/%Y %H:%M:%S")
                db.execute("INSERT INTO history ('user_id', 'stock', 'cost', 'datetime', 'share') VALUES (:user_id, :stock, :cost, :dt, :share)",
                           user_id=session["user_id"], cost=quoted_value["price"], share=share_value, stock=quoted_value["symbol"], dt=dt)

                return redirect("/")
            else:
                return apology("not enough cash to buy stocks", 403)
        else:
            # check if user have enough cash to purchase
            if current_money[0]["cash"] >= quoted_value["price"]:

                # add new purchase data to database
                db.execute("INSERT INTO purchase ('user_id', 'cost', 'share', 'name', 'stock') VALUES (:user_id, :cost, :share, :name, :stock)",
                           user_id=session["user_id"], cost=quoted_value["price"], share=share_value, name=quoted_value["name"], stock=quoted_value["symbol"])

                balance = round(current_money[0]["cash"] - (float(quoted_value["price"]) * int(share_value)), 2)

                db.execute("UPDATE users SET cash = :balance WHERE id = :current_user",
                           balance=balance, current_user=session["user_id"])

                now = datetime.now()
                dt = now.strftime("%d/%m/%Y %H:%M:%S")
                db.execute("INSERT INTO history ('user_id', 'stock', 'cost', 'datetime', 'share') VALUES (:user_id, :stock, :cost, :dt, :share)",
                           user_id=session["user_id"], cost=quoted_value["price"], share=share_value, stock=quoted_value["symbol"], dt=dt)

                return redirect("/")
            else:
                return apology("not enough cash to buy stocks", 403)
    else:
        # return buy.html page
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # query data from database to generate history reports
    reports = db.execute("SELECT * FROM history WHERE user_id = :current_user ORDER BY datetime DESC",
                         current_user=session["user_id"])

    # check if user have done any transactions yet
    if len(reports) == 0:
        return apology("You do not have done any transactions yet.")
    else:
        # render history.html page
        return render_template("history.html", reports=reports)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # check request method
    if request.method == "POST":

        # call lookup function to generate report from IEX
        quoted_value = lookup(request.form.get("symbol"))

        # check if qouted_value has returned some data
        if quoted_value == None:
            return apology("symbol does not exist", 403)
        else:
            # display data from lookup to quoted.html page
            value_name = quoted_value["name"]
            value_price = quoted_value["price"]
            value_symbol = quoted_value["symbol"]
            return render_template("quoted.html", name=value_name, symbol=value_symbol, price=value_price)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # setting variables
    new_user = request.form.get("username")
    new_email = request.form.get("email")
    new_password = request.form.get("password")
    new_confirmation = request.form.get("confirmation")

    # check request method
    if request.method == "POST":

        # Ensure username was submitted
        if not new_user:
            return apology("must provide username", 403)
        # Ensure email was submitted
        elif not new_email:
            return apology("must provide valid email", 403)

        # Ensure password was submitted
        elif not new_password:
            return apology("must provide password", 403)

        # Ensure password confirmation
        elif new_password != new_confirmation:
            return apology("must confirm you password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=new_user)

        # Ensure username uniqueness
        if len(rows) == 1:
            return apology("username already exist", 403)

        # used hash function to generate hash value of the password
        new_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)

        # add data to database
        db.execute("INSERT INTO users ('username', 'hash') VALUES (:username, :my_hash)", username=new_user, my_hash=new_hash)

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Check request method
    if request.method == "POST":
        quoted_value = lookup(request.form.get("symbol"))
        share_value = request.form.get("shares")

        # check input validity
        if quoted_value == None:
            return apology("provide valid symbol", 403)
        elif share_value == "" or int(share_value) <= 0:
            return apology("must provide the number of shares", 403)

        duplicates = db.execute("SELECT * FROM purchase WHERE name = :current AND user_id = :user_id",
                                current=quoted_value["name"], user_id=session["user_id"])
        current_money = db.execute("SELECT cash FROM users WHERE id = :current_user",
                                   current_user=session["user_id"])

        # check if user have stocks
        if len(duplicates) == 1:
            # check if users stocks if enough to sell
            if int(duplicates[0]["share"]) >= int(share_value):

                # same logic as buying but different operation
                new_share = int(duplicates[0]["share"]) - int(share_value)

                db.execute("UPDATE purchase SET share = :new_share WHERE name = :name AND user_id = :user_id",
                           new_share=new_share, name=quoted_value["name"], user_id=session["user_id"])

                balance = round(current_money[0]["cash"] + (float(quoted_value["price"]) * int(share_value)), 2)

                db.execute("UPDATE users SET cash = :balance WHERE id = :current_user",
                           balance=balance, current_user=session["user_id"])

                now = datetime.now()
                dt = now.strftime("%d/%m/%Y %H:%M:%S")
                db.execute("INSERT INTO history ('user_id', 'stock', 'cost', 'datetime', 'share') VALUES (:user_id, :stock, :cost, :dt, :share)",
                           user_id=session["user_id"], cost=quoted_value["price"], share="-"+share_value, stock=quoted_value["symbol"], dt=dt)

                return redirect("/")
            else:
                return apology("not enough shares to sell stocks", 403)
        else:
            return apology("no shares to sell stocks", 403)
    else:
        stocks = db.execute("SELECT * FROM purchase WHERE user_id = :current", current=session["user_id"])
        return render_template("sell.html", stocks=stocks)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def first_personal():
    """Personal Touch"""

    # set variables from inputs
    old_pass = request.form.get("old_password")
    new_pass = request.form.get("new_password")
    confirm = request.form.get("confirmation_new")

    # check request method
    if request.method == "POST":

        # Ensure old password was submitted
        if not old_pass:
            return apology("must provide your current password", 403)

        # Ensure password was submitted
        elif not new_pass:
            return apology("must provide new password", 403)

        # Ensure password confirmation
        elif new_pass != confirm:
            return apology("must confirm you password", 403)

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
        return render_template("password.html")


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def second_personal():
    """Personal Touch"""

    # set amount value from input
    amount = request.form.get("deposit")

    if request.method == "POST":

        # check valid input of amount
        if not amount or int(amount) <= 0:
            return apology("must provide valid amount", 403)
        else:
            # query database for the current cash balance
            rows = db.execute("SELECT cash FROM users WHERE id = :user_id",
                              user_id=session["user_id"])

            # set new cash amount
            new_amount = float(rows[0]["cash"]) + float(amount)

            # update users cash
            db.execute("UPDATE users SET cash = :current WHERE id = :user_id", current=new_amount, user_id=session["user_id"])

            return render_template("confirm.html", message="Cash Deposit Successful")

    else:
        return render_template("deposit.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
