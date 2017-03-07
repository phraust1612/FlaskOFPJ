from flask import *
from CPortal import *
import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)
app.secret_key = "testestestsetset"
portal = CPortal()

@app.route("/",methods=["GET","POST"])
def home():
    if 'user' in session:
        return redirect(url_for("mainpage"))
    return render_template('home.html')

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == 'POST':
        ID = request.form['id']
        PW = request.form['pw']
        global portal
        err = portal.SQLLogin(ID,PW)
        if err !=0:
            flash("Invalid Login!!!")
            return redirect(url_for("home"))
        session['user'] = ID
        portal.LoadMember()
        return redirect(url_for("mainpage"))
    return redirect(url_for("home"))

@app.route("/main/",methods=["GET","POST"])
def mainpage():
    if 'user' in session:
        return render_template('main.html')
    else:
        return redirect(url_for("home"))

@app.route("/main/submit",methods=["GET","POST"])
def submit():
    if request.method == 'POST':
        year = int(request.form['yr'])
        month = int(request.form['mth'])
        day = int(request.form['day'])
        prior = int(request.form['prior'])
        global portal
        err = portal.SubmitWish("",prior,year,month,day)
        if err==0:
            flash("Suceeded!!!")
        else:
            flash("Failed!!! : %s" % err)
    return redirect(url_for("mainpage"))
    
@app.route("/logout",methods=["GET"])
def logout():
    session.pop('user',None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host='172.22.55.148')
