import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import string
import calendar

from helpers import login_required, get_values, get_dates, get_target, get_statement, get_latest_entry, data_available, get_label, formatted, get_count, get_all_dates, count_months

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

@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    """Show homepage"""

    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['username']
    date = db.execute("SELECT startdate FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['startdate']

    if request.method == "POST":
        goal = request.form.get('goal')
    else:
        goal = 'weight'

    if not data_available(session['user_id']):
        nodata = True
        return render_template("index.html", username=username, date=date, nodata=nodata)

    #Pull data & dates from 'helper' functions
    dates = get_dates(goal) # x-axis
    values = get_values(goal) # y-axis
    label = get_label(goal) #get point label

    #pull target
    target_tmp = get_target(goal)
    target = []
    for i in range(0,len(dates)):
        target.append(target_tmp)
    if goal != 'bmi':
        goal = goal.capitalize()
    else:
        goal = goal.upper()

    nodata = False
    return render_template("index.html", username=username, date=date, dates=dates, values=values, target=target, goal=goal, nodata=nodata, label=label)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
 # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

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
    if not data_available(session['user_id']):
        nodata = True
        return render_template("dashboard.html", username=username, nodata=nodata)
    else:
        nodata = False

    goals = ['weight', 'bmi', 'speed','money']
    percents = []
    counts = []
    # Compare goals against their targets and get the percent achieved values
    for goal in goals:
        latest_entry = get_latest_entry(goal)
        target = get_target(goal)
        percent = round(latest_entry/target * 100, 2)
        percents.append(percent)
        
        
        goal_list_tmp = ['Weight', 'BMI', 'Speed', 'Money']
        # Find the goal corresponding with the highest perentage
        max_percent_index = percents.index(max(percents))
        max_percent_goal = goal_list_tmp[max_percent_index]
        

        # Find which goal is the furthest from reaching it's assigned target
        min_index = percents.index(min(percents))
        min_goal = goals[min_index]

        # Get Goal Counts
        count = get_count(goal)
        counts.append(count)
        
        max_index = counts.index(max(counts))
        
        max_goal = goal_list_tmp[max_index]
        
        min_index = counts.index(min(counts))
        min_goal_tmp = goal_list_tmp[min_index]
        
        # Get Dates
        dates = get_all_dates()
        
        # Count entries per month
        count_month = count_months()
        
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']
        highest_month_count = count_month.index(max(count_month))
        lowest_month_count = count_month.index(min(count_month))
        highest_month = months[highest_month_count]
        lowest_month = months[lowest_month_count]
        


    return render_template("dashboard.html", username=username, percents=percents, min_goal=min_goal, nodata=nodata, counts=counts, dates=dates, count_month = count_month, max_goal = max_goal, min_goal_tmp = min_goal_tmp, highest_month = highest_month, lowest_month = lowest_month, max_percent_goal = max_percent_goal)

@app.route("/data_add", methods=['GET','POST'])
@login_required
def data_add():
    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['username']
    return render_template("data_add.html", username=username)

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
        month = calendar.month_name[int(datetime.today().strftime('%m'))]

        ## Put the data into the db (goal, value, timestamp, session['user_id'], etc.)
        db.execute("INSERT INTO goals (id, goal, value, date, month) VALUES (:user_id, :goal, :value, :date, :month)",
                    user_id = int(session["user_id"]), goal = session['goal'], value = value, date = date, month = month)
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
        string = get_statement(session['goal']) #this is a helper function to return the correct form placeholder based on the goal

        #Render the correct amount of entry rows
        session['entries'] = int(request.form.get("entries"))

        #if entries exceed 24:
        if int(request.form.get("entries")) > 24:
            flash("# of Entries Cannot Exceed 24!")
            return redirect("/data_prev")

        entries = []
        i = 1
        while not i > session['entries']:
            entries.append(i)
            i=i+1

        return render_template("formaddon_old.html", goal=session['goal'], entries = entries, string=string)
    #if you clicked on "Add Previous Data" tab
    return render_template("data_prev.html")

@app.route("/formaddon_old", methods=["GET", "POST"])
@login_required
def formaddon_old():
    if request.method == "POST":

        # If a number gets entered properly
        values = ['value1','value2','value3','value4','value5','value6','value7','value8','value9','value10','value11','value12','value13','value14','value15','value16','value17','value18','value19','value20','value21','value22','value23','value24']
        dates = ['date1','date2','date3','date4','date5','date6','date7','date8','date9','date10','date11','date12','date13','date14','date15','date16','date17','date18','date19','date20','date21','date22','date23','date24']
        i = 0
        for value in values:
            if request.form.get(value) and request.form.get(dates[i]):
                date = request.form.get(dates[i])
                db.execute("INSERT INTO goals (id, goal, value, date, month) VALUES (:user_id, :goal, :value, :date, :month)",
                    user_id = int(session["user_id"]), goal = session['goal'],
                    value = request.form.get(value), date = date,
                    month = calendar.month_name[int(date[5:7])])
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

    #check if the old password correct
    if not check_password_hash(rows[0]["hash"], request.form.get("oldpw")):
        flash("Incorrect current password!")
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
    if request.method == "POST":
        target = request.form.get('target')
        value = request.form.get('value')

        if request.form.get('value') == None:
            flash('Error')
            return redirect("/targets")

        entry = db.execute("SELECT * FROM targets WHERE id = :user_id AND goal = :goal", user_id=session['user_id'], goal = target)
        if len(entry) == 0:
            db.execute("INSERT INTO targets (id, goal, value) VALUES (:user_id, :goal, :value)", user_id = session['user_id'], goal = target, value = value)
            flash("Target Added!")
        else:
            # Update target value
            db.execute("UPDATE targets SET value = :new_value WHERE id = :user_id AND goal = :goal",
            new_value = value, user_id = session['user_id'], goal = target)
            # Updates timestamp
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d")
            db.execute("UPDATE targets SET date = :new_date WHERE id = :user_id AND goal = :goal",
            new_date = dt_string, user_id = session['user_id'], goal = target)
            flash("Target Updated!")

    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id = session["user_id"])[0]['username']
    rows = db.execute("SELECT * FROM targets WHERE id = :user_id", user_id = session['user_id'])
    length = len(rows)
    return render_template("targets.html",username=username, rows=formatted(rows), length = length)

@app.route("/data_remove", methods = ['GET', 'POST'])
@login_required
def data_remove():
    if request.method == "GET":
        get = True
        return render_template("data_remove.html", get=get)
    get = False
    goal = request.form.get('goal')
    session['goal'] = goal
    if not goal:
        flash("Must select a goal!")
        return render_template("data_remove.html", get=True)

    rows = db.execute("SELECT * FROM goals where id = :user_id AND goal = :goal ORDER BY date", user_id = session['user_id'], goal = goal)
    return render_template("data_remove.html", length=len(rows), rows=formatted(rows), get=get, goal=goal)

@app.route("/data_removed/", methods = ['GET', 'POST'])
@login_required
def data_removed():
    if request.method == "GET":
        #Pulls JSON vector (as a string) which is a parameter submitted to the /data_removed/?[var]
        values = request.args.get('valueList')

        if values != None:
            #Cleaning up the string & ultimately converting it into a numerical list
            symbols = ['"','[',']']
            for symbol in symbols:
                values = values.replace(symbol,'')
            valueList = list((values.split(",")))
            numbers = []
            for value in valueList:
                numbers.append(int(value))

            session['numbers'] = numbers
            rows = db.execute("SELECT * FROM goals WHERE id = :user_id AND goal = :goal ORDER BY date", user_id=session['user_id'], goal=session['goal'])
            return render_template("data_removed_temp.html", numbers=session['numbers'], goal=session['goal'], rows=rows)

        flash("You must select at least one entry to delete!")
        return render_template("data_remove.html")

@app.route("/data_removed_temp", methods = ['GET', 'POST'])
@login_required
def data_removed_temp():
    if request.method == 'POST':
        rows = db.execute("SELECT * FROM goals WHERE id = :user_id AND goal = :goal ORDER BY date", user_id=session['user_id'], goal=session['goal'])
        numbers = session['numbers']
        for number in numbers:
            date = rows[number - 1]['date']
            db.execute("DELETE FROM goals WHERE id = :user_id AND goal = :goal AND date = :date", user_id = session['user_id'], goal = session['goal'], date = date)
        flash('Entries Successfully Deleted!')
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")