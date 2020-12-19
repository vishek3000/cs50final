import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required, get_values, get_dates

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
db = SQL("sqlite:///goals.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/")
@login_required
def index():
    """Show homepage"""
    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['username']
    date = db.execute("SELECT startdate FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['startdate']

    #Pull data & dates from 'helper' functions
    weight_dates = get_dates('weight') # x-axis
    weights = get_values('weight') # y-axis

    #pull money data
    money_dates = get_dates('money')
    money = get_values('money')

    return render_template("index.html", username=username, date=date, weight_dates=weight_dates, weights = weights, money_dates=money_dates, money=money)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
 # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")
            return render_template("register.html")

        # Ensure password was confirmed
        elif not request.form.get("con_password"):
            flash("must confirm password")
            return render_template("register.html")

        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        #Ensure passwords match
        if not check_password_hash(password, request.form.get("con_password")):
            flash("passwords must match!")
            return render_template("register.html")

         # Check if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        if (len(rows) > 0):
            flash("Username already exists!")
            return render_template("register.html")

        # If everything done properly
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        db.execute("INSERT INTO users (username, hash, startdate) VALUES (:username, :pw_hash, :date)", username=username, pw_hash = password, date = dt_string)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/dashboard")
@login_required
def dashboard():
    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['username']
    return render_template("dashboard.html", username=username)

@app.route("/addgoal", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        #error handler for no goal selected
        if not request.form.get("goal"):
            flash("Must select a goal!")
            return redirect("/addgoal")

        #Remember the goal that the user selected to be able to pass this into the '/formaddon' section
        session['goal'] = request.form.get("goal")
        return render_template("formaddon.html", goal=session['goal'])

    #if the page was reached by clicking a link to the page, etc.
    return render_template("addgoal.html")

@app.route("/formaddon", methods=["GET", "POST"])
@login_required
def formaddon():
    if request.method == "POST":
        # error handler for no value entered
        if not request.form.get("value"):
            flash("Must enter a value!")
            return redirect("/formaddon")

        #If a number gets entered properly
        value = request.form.get("value")
        date = datetime.today().strftime('%Y-%m-%d')

        ## Put the data into the db (goal, value, timestamp, session['user_id'], etc.)
        db.execute("INSERT INTO goals (id, goal, value, date) VALUES (:user_id, :goal, :value, :date)",
                    user_id = int(session["user_id"]), goal = session['goal'], value = value, date = date)
        # Take user back to homepage with confirmation
        flash("Data Submitted!")
        return redirect("/")

    #If the page was reached via a link (not fully possible)
    return render_template("formaddon.html")

@app.route("/data_prev", methods=["GET", "POST"])
@login_required
def data_prev():
    if request.method == "POST":
        #error handler for no goal selected
        if not request.form.get("goal"):
            flash("Must select a goal!")
            return redirect("/data_prev")
        #Remember the goal that the user selected to be able to pass this into the '/formaddon' section
        session['goal'] = request.form.get("goal")
        session['entries'] = int(request.form.get("entries"))
        return render_template("formaddon_old.html", goal=session['goal'])
    #if you clicked on "Add Previous Data" tab
    return render_template("data_prev.html")

@app.route("/formaddon_old", methods=["GET", "POST"])
@login_required
def formaddon_old():
    if request.method == "POST":

        # If a number gets entered properly
        values = ['value1','value2','value3','value4','value5','value6','value7','value8','value9','value10','value11','value12']
        dates = ['date1','date2','date3','date4','date5','date6','date7','date8','date9','date10','date11','date12']
        i = 0
        for value in values:
            if request.form.get(value) and request.form.get(dates[i]):
                db.execute("INSERT INTO goals (id, goal, value, date) VALUES (:user_id, :goal, :value, :date)",
                    user_id = int(session["user_id"]), goal = session['goal'],
                    value = request.form.get(value), date = request.form.get(dates[i]))
                i=i+1
            else:
                i=i+1
                continue
        flash("Data submitted!")
        return redirect("/")
    # if "GET"
    return render_template("formaddon_old.html")


@app.route("/edit")
@login_required
def edit():
    """allow to edit username & password"""
    # find the current users username
    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['username']
    return render_template("edit.html", username=username)

@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    """show form to change password"""
    if request.method == 'GET':
        return render_template("changepw.html")

    rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id = session['user_id'])

    #check if oldpw field entered
    if not request.form.get("oldpw"):
        flash("Must enter your current password!")
        return render_template("changepw.html")

    #check if the old password correct
    if not check_password_hash(rows[0]["hash"], request.form.get("oldpw")):
        flash("Incorrect current password!")
        return render_template("changepw.html")

    #check if newpw field entered
    if not request.form.get("newpw"):
        flash("Must enter a new password!")
        return render_template("changepw.html")

    #check if newpw_again field entered
    if not request.form.get("newpw_again"):
        flash("Must confirm your new password!")
        return render_template("changepw.html")

    #check if the new pw matches confirmation:
    new_pw = generate_password_hash(request.form.get("newpw"))
    if not check_password_hash(new_pw, request.form.get("newpw_again")):
        flash("New passwords must match!")
        return render_template("changepw.html")


    #check if new pw isn't the same as the old pw:
    if check_password_hash(rows[0]['hash'], request.form.get("newpw")):
        flash("New password cannot be the same as the old password!")
        return render_template("changepw.html")

    #if all inputs provided and match up:
    db.execute("UPDATE users SET hash = :new_hash WHERE id = :user_id",
    new_hash = new_pw, user_id = session["user_id"])
    flash("Password successfully updated!")
    return redirect("/")

@app.route("/changeuser", methods=["GET", "POST"])
@login_required
def changeuser():
    """show form to change username"""

    if request.method == "GET":
        return render_template("changeuser.html")

    #elif POST:

    #check if first field is blank
    if not request.form.get("newuser"):
        flash("Must enter a new username")
        return render_template("changeuser.html")

    #check if new username choice is != to old username
    current_username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['username']
    if request.form.get("newuser") == current_username:
        flash("New username cannot be equal to the current username!")
        return render_template("changeuser.html")

    #check if new username is already in database
    rows = db.execute("SELECT * FROM users WHERE username = :new_username", new_username = request.form.get("newuser"))
    if len(rows) != 0:
        flash("This username is already taken, please try another name")
        return render_template("changeuser.html")

    #check if second field is blank
    if not request.form.get("newuser_again"):
        flash("Must confirm new user name!")
        return render_template("changeuser.html")

    #check if the fields are equal
    if request.form.get("newuser") != request.form.get("newuser_again"):
        flash("Usernames must match!")
        return render_template("changeuser.html")

    #if success:
    db.execute("UPDATE users SET username = :new_name WHERE id = :user_id",
    new_name = request.form.get("newuser"), user_id = session["user_id"])
    flash("Username successfully changed!")
    return redirect("/")

@app.route("/targets", methods=["GET","POST"])
@login_required
def targets():
    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session["user_id"])[0]['username']
    rows = db.execute("SELECT * FROM targets WHERE id = :user_id", user_id = session['user_id'])
    length = len(rows)
    if request.method == "POST":
        target = request.form.get('target')
        value = request.form.get('value')
        entry = db.execute("SELECT * FROM targets WHERE id = :user_id AND goal = :goal", user_id=session['user_id'], goal = target)
        if len(entry) == 0:
            db.execute("INSERT INTO targets (id, goal, value) VALUES (:user_id, :goal, :vlae)", username=username, pw_hash = password, date = dt_string)
    
        
        
        
        
    return render_template("targets.html",username=username, rows=rows, length = length)




@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")