# This is my README file for my CS50 Final Project: GoalSetter+

## High Level description: 
This web application has been designed with HTML, CSS, Javascript (chart.js), Python, Flask & SQL.
The main purpose of this web application is to allow users to input & track goals against user defined targets. Think of it as a digital
'logbook' to keep track of your goals. Given that this web application is in it's early stages of development, the system currently consists
of 4 pre-defined goals: Weight, BMI, money & speed. Users have the option to delete entries, edit targets, change usernames & passwords.
The website has also been designed with responsiveness in mind.

## Key Learning Outcomes
* Full stack development using Flask as a controller
* Database management & querying with SQL (specifically utilizing sqlite3)
* Responsive design using CSS
* Data visualization using Javascript & chart.js
* Error handling and edge-case testing


## Follow these steps to successfully set up the database:
1. Clone this entire repository
2. cd into the parent folder "project/"
3. In the terminal window, run the following to set up the databases:

```bash
.sqlite3 goals.db
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username VARCHAR(255) NOT NULL, hash VARCHAR(255) NOT NULL, startdate VARCHAR(255) NOT NULL);
CREATE TABLE goals (id INTEGER, goal TEXT, value INTEGER, date DATETIME, Month TEXT);
CREATE TABLE targets (id INTEGER, goal TEXT, value FLOAT, date DATE);
.quit
```



## Upon logging in / registering, the web application consists of 4 main tabs:
* Set Targets
* Add Data
* Remove Data
* Dashboard

### Follow these next steps to successfully set up your user account:
1. Click on the "Set Targets" tab and enter your targets for the goals
2. Go to the "Add Data" page and enter any data you may have previously recorded against these goals, or enter new data from today
3. After completing steps 1 & 2, your charts will show up on the homepage, and you can now view your summary stats on the "Dashboard" page
4. You also have the choice to remove data, change your username or your password. EnjoY!
