from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL



app=Flask(__name__)


app.secret_key="travel_secret_key"
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='902165'
app.config['MYSQL_DB']='travel_booking'

mysql=MySQL(app)



@app.route("/")
def home():
    return render_template("home.html")
@app.route("/destination")
def destination():
    return render_template("destination.html")
@app.route("/booking")
def booking():
    return render_template("booking.html")

                                                          #   login
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":
      email=request.form['email']
      password=request.form['password']
      cur=mysql.connection.cursor()
    
    cur.execute(
        "SELECT * FORM usersWHER email=%s AND password=%s"
        (email,password)
    )

    user =cur.fetchone()
    if user:
        session['user_id']= user[0]
        session['user_name']= user[1]
        return redirect("/dashboard")
    
    return render_template("login.html")

                                                             # signup

@app.route("/signup",methods=["GET" ,"POST"])
def signup():

    if request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        phone=request.form['phone']
        confirm_password= request.form['confirm_password']

        if password != confirm_password:
            return "password do not match !"

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",(email,)
        )
        user =cur.fetchone()

        if user:
            cur.close()
            return"Email already exists !"
        
        cur.execute(
            "INSERT INTO users(name,email,phone,password) VALUES (%s,%s,%s,%s)",(name,email,phone,password)
        )
        mysql.connection.commit()
        cur.close()

        return redirect("/login")


    return render_template("signup.html")

                                                            # dashboard 

@app.route("/dashboard")
def dashboard():

    if 'user_id' not in session:
        return redirect("/login")
    return render_template("dashboard.html", username=session['user_name'])

@app.route("/my_booking")
def my_booking():
    return render_template("my_booking.html")
@app.route("/profile")
def profile():
   return render_template("profile.html")



@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/packages")
def packages():
    return render_template("packages.html")


if __name__=="__main__":
    app.run(debug=True)
