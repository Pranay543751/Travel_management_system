from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os

import email
import csv
from flask import Response
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
                           upcoming_trips=upcoming,
                           completed_trips=completed,
                           recent_bookings=recent_bookings)


@app.route("/my_booking")
def my_booking():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id,user_id,destination, travel_date, travelers,
               package_type, amount, status
        FROM bookings
        WHERE user_id=%s
        ORDER BY id DESC
    """, (user_id,))

    bookings = cur.fetchall()

    cur.close()

    return render_template(
        "my_booking.html",
        bookings=bookings
    )


@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )

    user = cur.fetchone()

    cur.close()

    if not user:
        return "User not found"

    return render_template(
        "profile.html",
        user=user
    )



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

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    # Total Users
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    # Total Bookings
    cur.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cur.fetchone()[0]

    # Total Revenue
    cur.execute("SELECT IFNULL(SUM(amount),0) FROM bookings WHERE status='Completed'")
    revenue = cur.fetchone()[0]

    # Pending Bookings
    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'")
    pending = cur.fetchone()[0]

    # Confirmed Bookings
    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'")
    confirmed = cur.fetchone()[0]

    # Cancelled Bookings
    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'")
    cancelled = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Confirmed'")
    confirmed = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Completed'")
    completed = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'")
    cancelled = cur.fetchone()[0]
    # Recent Bookings
    cur.execute("""
        SELECT id,destination,travel_date,status
        FROM bookings
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_bookings = cur.fetchall()
    monthly_revenue = []

    for month in range(1,13):

        cur.execute("""

        SELECT IFNULL(SUM(amount),0)

        FROM bookings

        WHERE MONTH(travel_date)=%s

        """,(month,))

    monthly_revenue.append(cur.fetchone()[0])

    cur.close()
    cur.execute("SELECT COUNT(*) FROM contact_messages")
    total_messages = cur.fetchone()[0]
    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
    total_bookings=total_bookings,
    revenue=revenue,
    total_messages=total_messages,
    recent_bookings=recent_bookings,

    pending=pending,
    confirmed=confirmed,
    completed=completed,
    cancelled=cancelled,

    monthly_revenue=monthly_revenue
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
        users=users,
        search=search
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

@app.route("/edit-user/<int:user_id>", methods=["GET","POST"])
def edit_user(user_id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    if request.method=="POST":

        name=request.form["name"]
        email=request.form["email"]
        phone=request.form["phone"]

        cur.execute("""
        UPDATE users
        SET
        name=%s,
        email=%s,
        phone=%s
        WHERE id=%s
        """,
        (name,email,phone,user_id))

        mysql.connection.commit()

        cur.close()

        return redirect("/manage-users")

    cur.execute(
        "SELECT * FROM users WHERE id=%s",
        (user_id,)
    )

    user=cur.fetchone()

    cur.close()

    return render_template(
        "edit_user.html",
        user=user
    )

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



@app.route("/delete-booking-admin/<int:id>")
def delete_booking_admin(id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM bookings WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect("/manage-bookings")

@app.route("/edit-booking-admin/<int:id>", methods=["GET","POST"])
def edit_booking_admin(id):

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    if request.method=="POST":

        destination=request.form["destination"]
        date=request.form["travel_date"]
        travelers=request.form["travelers"]
        amount=request.form["amount"]
        status=request.form["status"]

        cur.execute("""
        UPDATE bookings
        SET
        destination=%s,
        travel_date=%s,
        travelers=%s,
        amount=%s,
        status=%s
        WHERE id=%s
        """,
        (
            destination,
            date,
            travelers,
            amount,
            status,
            id
        ))

        mysql.connection.commit()

        cur.close()

        return redirect("/manage-bookings")

    cur.execute(
        "SELECT * FROM bookings WHERE id=%s",
        (id,)
    )

    booking=cur.fetchone()

    cur.close()

    return render_template(
        "edit_booking_admin.html",
        booking=booking
    )

@app.route("/export-bookings")
def export_bookings():

    if "admin_id" not in session:
        return redirect("/admin-login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
        id,
        user_id,
        destination,
        travel_date,
        travelers,
        amount,
        status
        FROM bookings
    """)

    bookings = cur.fetchall()

    cur.close()

    def generate():

        data = csv.writer(open("dummy.csv", "w", newline=""))

        yield "ID,User ID,Destination,Travel Date,Travelers,Amount,Status\n"

        for booking in bookings:

            yield f"{booking[0]},{booking[1]},{booking[2]},{booking[3]},{booking[4]},{booking[5]},{booking[6]}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=bookings.csv"
        }
    )


@app.route("/change-admin-password", methods=["GET", "POST"])
def change_admin_password():

    if "admin_id" not in session:
        return redirect("/admin-login")

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM admin WHERE id=%s AND password=%s",
            (session["admin_id"], current_password)
        )

        admin = cur.fetchone()

        if not admin:
            cur.close()
            return "Current Password is Incorrect"

        if new_password != confirm_password:
            cur.close()
            return "New Password and Confirm Password do not match"

        cur.execute(
            "UPDATE admin SET password=%s WHERE id=%s",
            (new_password, session["admin_id"])
        )

        mysql.connection.commit()
        cur.close()

        return redirect("/admin-profile")

    return render_template("change_admin_password.html")

@app.route("/download-invoice/<int:booking_id>")
def download_invoice(booking_id):

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT users.name,
               users.email,
               bookings.destination,
               bookings.travel_date,
               bookings.travelers,
               bookings.amount,
               bookings.status
        FROM bookings
        JOIN users
        ON bookings.user_id = users.id
        WHERE bookings.id=%s
    """, (booking_id,))

    booking = cur.fetchone()
    cur.close()

    if not booking:
        return "Booking Not Found"

    filename = f"invoice_{booking_id}.pdf"

    pdf = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b><font size=18>TravelHub Invoice</font></b>", styles["Title"])
    )

    elements.append(
        Paragraph(f"<b>Invoice No :</b> INV-{booking_id}", styles["Normal"])
    )

    elements.append(
        Paragraph("<br/>", styles["Normal"])
    )

    data = [
        ["Customer Name", booking[0]],
        ["Email", booking[1]],
        ["Destination", booking[2]],
        ["Travel Date", str(booking[3])],
        ["Travelers", booking[4]],
        ["Amount", f"₹ {booking[5]}"],
        ["Status", booking[6]],
    ]

    table = Table(data, colWidths=[2.5 * inch, 3.5 * inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)

    pdf.build(elements)

    return send_file(
        filename,
        as_attachment=True
    )

@app.route("/logout")
def logout():
    return render_template("logout.html")


@app.route("/logout-confirm")
def logout_confirm():

    session.clear()

    return redirect("/login")


if __name__=="__main__":
    app.run(debug=True)
