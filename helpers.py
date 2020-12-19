import os
import requests
import urllib.parse
from cs50 import SQL

from flask import redirect, render_template, request, session
from functools import wraps

db = SQL("sqlite:///goals.db")

def get_values(goal):
    value_list = db.execute("SELECT value FROM goals WHERE id = :user_id AND goal = :goal ORDER BY date", user_id = session['user_id'], goal = goal)
    values = []
    for x in range(0,len(value_list)):
        values.append(value_list[x]['value'])
    return values


def get_dates(goal):
    date_list = db.execute("SELECT date FROM goals WHERE id = :user_id AND goal = :goal ORDER BY date", user_id = session['user_id'], goal = goal)
    dates = []
    for x in range(0,len(date_list)):
        dates.append(date_list[x]['date'])
    return dates

def get_target(goal):
    target = db.execute("SELECT value FROM targets WHERE id = :user_id AND goal = :goal", user_id = session['user_id'], goal = goal)[0]['value']
    return target

def get_count(goal):
    count = db.execute("SELECT COUNT(goal) FROM goals WHERE id = :user_id AND goal = :goal", goal = goal, user_id=session['user_id'])[0]["COUNT(goal)"]
    return count


def get_statement(input_str):
    if input_str == 'weight':
        string = 'Weight [lbs]'
    elif input_str == 'bmi':
        string = 'BMI [m/h^2]'
    elif input_str == 'speed':
        string = 'Speed [m/s]'
    elif input_str == 'money':
        string = '$ Saved [$ CAD]'
    return string

def get_latest_entry(goal):
    entry_list = db.execute("SELECT value FROM goals WHERE goal = :goal AND id = :user_id ORDER BY date DESC", goal = goal, user_id = session['user_id'])[0]['value']
    return entry_list

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def data_available(user_id):
    """ Checks if there is data in the goals & targets databases """
    goal_list = ['weight','bmi','speed','money']
    checksum = 0
    for goal in goal_list:
        goals = db.execute("SELECT * FROM goals WHERE id = :user_id AND goal = :goal", user_id=user_id, goal=goal)
        targets = db.execute("SELECT * FROM targets WHERE id = :user_id AND goal = :goal", user_id=user_id, goal=goal)
        if (len(goals) > 0) and (len(targets) > 0):
            checksum = checksum + 1
        else:
            continue

    if checksum == 4:
        return True
    else:
        return False

def get_label(goal):
    if goal == 'weight':
        string = 'Weight [lbs]'
    elif goal == 'bmi':
        string = 'BMI [kg/m^2]'
    elif goal == 'speed':
        string = 'Speed [m/s]'
    elif goal == 'money':
        string = '$ CAD'
    return string

def formatted(rows):
    for row in rows:
        if row['goal'] == 'weight':
            row['value'] = f"{row['value']} lbs"
        elif row['goal'] == 'money':
            row['value'] = f"${row['value']:,.2f}"
        elif row['goal'] == 'speed':
            row['value'] = f"{row['value']} m/s"
        elif row['goal'] == 'bmi':
            row['value'] = f"{row['value']} kg/m^2"
        row['goal'] = row['goal'].capitalize()
    return rows

def get_all_dates():
    entries = db.execute("SELECT date FROM goals WHERE id = :user_id",user_id = session['user_id'])
    dates = []
    for entry in entries:
        dates.append(entry['date'])
    return dates

def count_months():
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October','November', 'December']
    counts = []
    for month in months:
        count = len(db.execute("SELECT * FROM goals where id = :user_id AND month = :month", user_id=session['user_id'], month=month))
        counts.append(count)
    return counts