import email

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
                SELECT id,destination,travel_date,travelers,package_type,amount,status
                FROM bookings
                WHERE user_id=%s
                ORDER BY id DESC""",(session["user_id"],))
    
    booking=cur.fetchall()
    cur.close()
    
    return render_template("my_booking.html", bookings=booking)



@app.route("/profile")
def profile():
   return render_template("profile.html")



@app.route("/contact",methods=["GET", "POST"])
def contact():

    if request.method=="POST":

        name=request.form["name"]
        email=request.form["email"]
        subject=request.form["subject"]
        message=request.form["message"]

        cur=mysql.connection.cursor()

        cur.execute("""
                    INSERT INTO contact_messages
                    (name,email,subject,message)
                    VALUES (%s,%s,%s,%s)
                    """, (name, email, subject, message))
        mysql.connection.commit()
        cur.close()

        return redirect("/contact")
    return render_template("contact.html")

@app.route("/contact-messages")
def contact_messages():

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id,
               name,
               email,
               subject,
               message
        FROM contact_messages
        ORDER BY id DESC
    """)

    messages = cur.fetchall()

    cur.close()

    return render_template(
        "contact_messages.html",
        messages=messages
    )

@app.route("/delete-message/<int:id>")
def delete_message(id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM contact_messages WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect("/contact-messages")


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



@app.route("/edit-booking/<int:booking_id>", methods=["GET","POST"])
def edit_booking(booking_id):

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    if request.method == "POST":

        travel_date = request.form["travel_date"]
        travelers = request.form["travelers"]
        package_type = request.form["package"]

        # Package ke hisab se amount
        if package_type == "Basic":
            amount = 9999
        elif package_type == "Premium":
            amount = 19999
        else:
            amount = 29999

        cur.execute("""
            UPDATE bookings
            SET travel_date=%s,
                travelers=%s,
                package_type=%s,
                amount=%s
            WHERE id=%s AND user_id=%s
        """,
        (
            travel_date,
            travelers,
            package_type,
            amount,
            booking_id,
            session["user_id"]
        ))

        mysql.connection.commit()
        cur.close()

        return redirect("/my-bookings")

    cur.execute("""
        SELECT destination,
               travel_date,
               travelers,
               package_type
        FROM bookings
        WHERE id=%s AND user_id=%s
    """,
    (
        booking_id,
        session["user_id"]
    ))

    booking = cur.fetchone()

    cur.close()

    return render_template(
        "edit_booking.html",
        booking=booking,
        booking_id=booking_id
    )
print(app.config["MYSQL_DB"])

@app.route("/admin-login", methods=["GET","POST"])
def admin_login():

    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        cur =mysql.connection.cursor()
        

        cur.execute("SELECT * FROM admin")
        print(cur.fetchall())
        cur.execute(
            "SELECT * FROM admin WHERE email=%s AND password=%s",(email,password)
        )
        admin=cur.fetchone()
        print("email",email)
        print("password",password)
        print("Admin",admin)
        cur.close()

        if admin:
            session["admin_id"]=admin[0]
            session["admin_name"]=admin[1]

            print(session)
            return redirect("/admin-dashboard")
        return "Invalid Email and Password"
    
    return render_template("admin_login.html")
@app.route("/admin-dashboard")
def admin_dashboard():

    print(session)

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cur.fetchone()[0]

    cur.execute("SELECT SUM(amount) FROM bookings")
    revenue = cur.fetchone()[0]

    if revenue is None:
        revenue = 0

    cur.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cur.fetchone()[0]
    
    cur.execute("""
              SELECT id,
                destination,
                 travel_date,
                status
                FROM bookings
                ORDER BY id DESC
                LIMIT 5
                """)

    recent_bookings = cur.fetchall()
    cur.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_bookings=total_bookings,
        revenue=revenue,
        total_messages=total_messages,
        recent_bookings=recent_bookings
    )

@app.route("/manage-users")
def manage_users():

    if "admin_id" not in session:
        return redirect("/admin-login")

    search=request.args.get("search","")

    cur=mysql.connection.cursor()

    cur.execute("""
    SELECT * FROM users
    WHERE name LIKE %s
    OR email LIKE %s
    """,
    ("%"+search+"%","%"+search+"%"))

    users=cur.fetchall()

    cur.close()

    return render_template(
        "manage_users.html",
        users=users
    )


@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):

    if "admin_id" not in session:
        return redirect("/admin-login")
    
    cur=mysql.connection.cursor()

    cur.execute("DELETE FROM users WHERE id=%s", (user_id))

    mysql.connection.commit()
    cur.close()

    return redirect("/manage-users")

@app.route("/delete-message/<int:id>")
def delete_message(id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur=mysql.connection.cursor()

    cur.execute(
        "DELETE FROM contact_messages WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect("/contact-messages")


@app.route("/update-booking-status/<int:id>", methods=["POST"])
def update_booking_status(id):
    if "admin_id" not in session:
        return redirect("/admin-login")

    status=request.form["status"]
    cur=mysql.connection.cursor()
    cur.execute("UPDATE bookings SET status=%s WHERE id=%s",(status,id)
                )

    mysql.connection.commit()
    cur.close()

    return redirect("/manage-bookings")

@app.route("/manage-bookings")
def manage_bookings():

    if "admin_id" not in session:
        return redirect("/admin-login")

    search = request.args.get("search", "")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM bookings
        WHERE destination LIKE %s
    """, ("%"+search+"%",))

    bookings = cur.fetchall()

    cur.close()

    return render_template(
        "manage_bookings.html",
        bookings=bookings
    )

@app.route("/change-admin-password",methods=["GET","POST"])
def change_admin_password():

    if "admin_id" not in session:
        return redirect("/admin-login")

    if request.method=="POST":

        old=request.form["old_password"]
        new=request.form["new_password"]

        cur=mysql.connection.cursor()

        cur.execute("""
        SELECT *
        FROM admin
        WHERE id=%s
        AND password=%s
        """,
        (session["admin_id"],old))

        admin=cur.fetchone()

        if admin:

            cur.execute("""
            UPDATE admin
            SET password=%s
            WHERE id=%s
            """,
            (new,session["admin_id"]))

            mysql.connection.commit()

            cur.close()

            return "Password Updated Successfully"

        return "Old Password Incorrect"

    return render_template("change_password.html")

@app.route("/admin-profile")
def admin_profile():

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM admin WHERE id=%s",
        (session["admin_id"],)
    )

    admin = cur.fetchone()

    cur.close()

    return render_template(
        "admin_profile.html",
        admin=admin
    )

if __name__=="__main__":
    app.run(debug=True)
