from flask import Flask, render_template, redirect, url_for, request, session, flash #import all of the important features
import sqlite3
import re
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'

def get_db_connection():  #connects the database with the program
    conn = sqlite3.connect('SurfBoards.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST']) #login route section
def login():
    msg = ''
    if request.method == 'POST':          # connects the database with the program to select everthing from users
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("SurfBoards.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username = ? and password = ?", (username, password))
        user = cur.fetchone()
        conn.close()
        if user: # if the users log in details are correct 
            session['loggedin'] = True
            session['user_id'] = user[0]
            session['username'] = user[1] # makes the user in session
            session['cart'] = []   #takes them to the surfboards page
            return redirect(url_for('surfboards'))
        else:
            msg = 'Invalid username or password' # displays message if wrong
    return render_template("login.html", message=msg)



@app.route("/logout") # route for logging out the user 
def logout():
    session.clear() # clears the persons session 
    return redirect(url_for("lobby"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST': # gets the method to post so featching the data 
        username = request.form['username']
        password = request.form['password']
        if not re.match(r'^[A-Za-z0-9]+$', username): # displays the message if not matched with the right indentaion
            msg = 'Only can Have letters and numbers' #displays the message 
        elif not re.match(r'^[A-Za-z0-9]+$', password):
            msg = 'Only can have letters and numbers'
        else:
            conn = sqlite3.connect("SurfBoards.db") # connects the databse with the program 
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE username = ?", (username,)) # selects everything from user 
            user = cur.fetchone()
            if user:
                msg = 'Username already exists' #displays message 
            else:
                cur.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password)) #inserts values into the database into users table 
                conn.commit()
                msg = 'Account Created' 
            conn.close()
    return render_template("signup.html", message=msg)


@app.route('/')
def layout(): # starting screen to display lobby 
    return render_template("lobby.html")


@app.route('/surfboard') 
def surfboards():
    conn = sqlite3.connect("SurfBoards.db") # connects the database with program
    cur = conn.cursor()
    cur.execute("SELECT * FROM SurfBoards") #gets everthing from surfboards
    surfboards = cur.fetchall()
    conn.close() #closes the connection
    return render_template("surfboards.html", surfboards=surfboards)


@app.route('/checkout', methods=['GET', 'POST']) # gets and post data from database 
def checkout():
    conn = get_db_connection()
    cur = conn.cursor()
    cart_items = session.get('cart', []) # for person in sessions make cart items 
    surfboards = []
    final_total = 0 # final total to equal to zero

    for item in cart_items:
        cur.execute("SELECT * FROM SurfBoards WHERE surfboard_id = ?", (item['surfboard_id'],)) # selects everthing from surfboards with item = surfboard_id
        surfboard = cur.fetchone()
        if surfboard:
            surfboard_dict = { # surfboard dictonary from database to make it easir 
                'surfboard_id': surfboard['surfboard_id'],
                'name': surfboard['surfboard_name'],
                'type': surfboard['surfboard_type'],
                'condition': surfboard['surfboard_condtion'],
                'price': surfboard['purchase_price'],
                'image': surfboard['surfboard_photo'],
                'quantity': item['quantity']
            }
            final_total += surfboard['purchase_price'] * item['quantity'] # final total will be purchase price multipled the item quanity 
            surfboards.append(surfboard_dict) # end the dictonary by making single line

    conn.close()

    return render_template('checkout.html', cart=surfboards,  
                           final_total=final_total)


@app.route('/<int:surfboard_id>/remove_from_cart', methods=['POST']) # removes from cart but still holding the id value
def remove_from_cart(surfboard_id):
    cart_items = session.get('cart', []) # sessions gets from the users 
    cart_items = [item for item in cart_items 
        if item['surfboard_id'] != surfboard_id] # for items in cart if item
    session['cart'] = cart_items
    return redirect(url_for('checkout')) #redirect to checkout with the removal 


@app.route('/surfboards/brand/<brand_name>') # fliter the brand name with the surfboards
def surfboards_by_brand(brand_name):
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM SurfBoards WHERE surfboard_name LIKE ?", # selects everything from the surboard table where surfboard names
        ('%' + brand_name + '%',)
    )
    surfboards = cur.fetchall()
    conn.close()
    return render_template( #returns the surfboards .html 
        "surfboards.html",
        surfboards=surfboards,
        brand_name=brand_name
    )


@app.route('/brands')
def brands():
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute("SELECT *  FROM Brands")
    brands = cur.fetchall()
    conn.close()
    return render_template("brands.html", brands=brands)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route('/purchase_products', methods=['POST']) #purschase prodcut in the cart section
def purchase_products():
    cart_items = session.get('cart', [])  #gets the users cart sessions
    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session.get('user_id', None)
    for item in cart_items:
        cur.execute("SELECT surfboard_name, purchase_price FROM SurfBoards WHERE surfboard_id = ?", # selects surfboard name etc from the surboards table   
                     (item['surfboard_id'],))
        surfboard = cur.fetchone()
        if surfboard:
            surfboard_name = surfboard['surfboard_name'] # making it able to store them in the database
            purchase_price = surfboard['purchase_price']
            if user_id:
                cur.execute #excutes the command
    ("INSERT INTO Checkout (user_id, surfboard_id, surfboard_name, purchase_price) VALUES (?, ?, ?, ?)",  #inserts the the id etc into the checkout with on what the user valued 
     (user_id, item['surfboard_id'], surfboard_name, purchase_price))
    conn.commit()
    conn.close()
    session['cart'] = []  # makes the session disaper with the cart empty 
    flash('Thank you for your purchase!') #flashes the message 
    flash('Please come to the nearest workshop for payment')
    return redirect(url_for('checkout'))
    
@app.route('/<int:surfboard_id>/add_to_cart', methods=["POST", "GET"]) # function fro adding to cart with surfbaord value 
def add_to_cart(surfboard_id):
    cart_items = session.get('cart', []) 
    item_in_cart = next((item for item in cart_items if item['surfboard_id'] == surfboard_id), None)
    if item_in_cart:
        item_in_cart['quantity'] += 1 # adds the item to cart with a count to go up by one in the quantity 
    else:
        cart_items.append({'surfboard_id': surfboard_id, 'quantity': 1}) #updateds it in teh cart items
    session['cart'] = cart_items  
    return redirect(url_for('checkout')) 

@app.route('/lobby') #lobbys screen
def lobby():
    return render_template("lobby.html")


@app.route('/rent')
def rent():
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM SurfBoards")
    surfboards = cur.fetchall()
    conn.close()
    return render_template("rent.html", surfboards=surfboards)



@app.route('/confirm_rental/<int:surfboard_id>', methods=['POST'])
def confirm_rental(surfboard_id):
    rental_date = request.form['rental_date']
    conn = sqlite3.connect("SurfBoards.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Rentals (user_id, surfboard_name, rental_date) VALUES (?, ?, ?)",
        (None, surfboard_id, rental_date)
    )
    conn.commit()
    conn.close()

    flash(f'Thank you for renting please be at Summer Beach on {rental_date}.')
    flash('Please exit if done')
    return redirect(url_for('rent'))




if __name__ == "__main__":
    app.run(debug=True)