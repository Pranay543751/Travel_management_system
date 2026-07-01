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




@app.route("/booking",methods=["GET","POST"])
def booking():
    if "user_id" not in session:
        return redirect("/login")
    
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        phone=request.form["phone"]
        destination=request.form["destination"]
        travel_date=request.form["travel_date"]
        travelers=request.form["travelers"]
        package=request.form["package"]
        message=request.form["message"]

        if package=="Basic":
            amount=9999
        elif package=="premium":
            amount=19999
        else:
            amount=29999

        cur=mysql.connection.cursor()

        status="Confirmed"

        cur.execute("""
                    INSERT INTO bookings
                    (user_id,name,email,phone,destination
                    ,travel_date,travelers,package_type,message,amount,status)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, 
                    (session["user_id"], name, email, phone, destination, travel_date, travelers, package, message, amount, status))
        mysql.connection.commit()
        cur.close()
        return redirect("/my_booking")
    return render_template("booking.html")






@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cur.fetchone()
        cur.close()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect("/dashboard")

        else:
            return "Invalid Email or Password"

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

        cur.execute("SELECT DATABASE();")
        print("Current DB :",cur.fetchone())

        cur.execute("SHOW COLUMNS FROM users;")
        print("Columns:",cur.fetchall())

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
    
    user_id=session["user_id"]

    cur=mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM bookings WHERE user_id=%s",(user_id,)
                )
    total_trips=cur.fetchone()[0]

    cur.execute("""
                SELECT COUNT(*) FROM bookings
                WHERE user_id=%s
                AND travel_date >= CURDATE()
                """,(user_id,))
    
    upcoming=cur.fetchone()[0]
    cur.execute(
        """
        SELECT COUNT(*) FROM bookings
        WHERE user_id=%s
        AND travel_date < CURDATE()
        """,
        (user_id,)
    )
    completed=cur.fetchone()[0]
    cur.execute("""
        SELECT destination,
               travel_date,
               status
        FROM bookings
        WHERE user_id=%s
        ORDER BY id DESC
        LIMIT 5
    """, (user_id,))

    recent_bookings = cur.fetchall()

    cur.close()



    return render_template("dashboard.html", username=session['user_name'],total_trips=total_trips,
                           upcoming=upcoming,
                           completed=completed,
                           recent_bookings=recent_bookings)


@app.route("/my_booking")
def my_booking():
    if "user_id" not in session:
        return redirect("/login")
    
    cur=mysql.connection.cursor()
    cur.execute("""
                SELECT destination,travel_date,travelers,package_type,amount,status
                FROM bookings
                WHERE user_id=%s
                ORDER BY id DESC""",(session["user_id"],))
    
    booking=cur.fetchall()
    cur.close()
    
    return render_template("my_booking.html", bookings=booking)



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




@app.route("/cancel-booking/<int:booking_id>")
def cancel_booking(booking_id):
    if "user_id" not in session:
        return redirect("/login")
    
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE bookings SET status='Cancelled' WHERE id=%s AND user_id=%s",
        (booking_id, session["user_id"])
    )
    mysql.connection.commit()
    cur.close()
    
    return redirect("/my_booking")


if __name__=="__main__":
    app.run(debug=True)
