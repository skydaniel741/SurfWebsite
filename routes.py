from flask import Flask, render_template, redirect, url_for, request, session, jsonify, flash
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey'

def get_db_connection():
    conn = sqlite3.connect('SurfBoards.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username = ? and password = ?", (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session['loggedin'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['cart'] = []  # Initialize cart in session
            return redirect(url_for('surfboards'))
        else:
            msg = 'Invalid username or password'
    return render_template("login.html", message=msg)

@app.route('/surfboards_data')
def surfboards_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM SurfBoards")
    surfboards = cur.fetchall()
    conn.close()
    surfboard_list = []
    for row in surfboards:
        surfboard = {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "condition": row[3],
            "price": row[4],
            "image": row[5],
        }
        surfboard_list.append(surfboard)
    return jsonify(surfboard_list)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("lobby"))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not re.match(r'^[A-Za-z]+$', username):
            msg = 'Invalid Username Try Again'
        elif not re.match(r'^[A-Za-z0-9]+$', password):
            msg = 'Invalid Password Try Again'
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
            user = cur.fetchone()
            if user:
                msg = 'Username already exists'
            else:
                cur.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                msg = 'Account Created'
            conn.close()
    return render_template("signup.html", message=msg)

@app.route('/<int:surfboard_id>/add_to_cart', methods=["POST", "GET"])
def add_to_cart(surfboard_id):
    if 'loggedin' not in session:
        flash('You must be logged in to add items to cart', category="danger")
        return redirect(url_for("login"))

    cart_items = session.get('cart', [])

    # Check if the surfboard is already in the cart
    item_in_cart = next((item for item in cart_items if item['surfboard_id'] == surfboard_id), None)

    if item_in_cart:
        # Increment the quantity if it exists in the cart
        item_in_cart['quantity'] += 1
    else:
        # Add a new item to the cart
        cart_items.append({'surfboard_id': surfboard_id, 'quantity': 1})
    
    session['cart'] = cart_items  # Update the cart in the session
    
    return redirect(url_for('surfboards'))  # Ensure this matches your route definition

@app.route('/')
def layout():
    return render_template("lobby.html")

@app.route('/surfboard')
def surfboards():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM SurfBoards")
    surfboards = cur.fetchall()
    conn.close()
    return render_template("surfboards.html", surfboards=surfboards)

@app.route('/<int:surfboard_id>/remove_from_cart', methods=['POST'])
def remove_from_cart(surfboard_id):
    if 'loggedin' not in session:
        flash('You must be logged in to remove items from the cart', category="danger")
        return redirect(url_for('login'))

    cart_items = session.get('cart', [])

    # Remove the item from the cart if it exists
    cart_items = [item for item in cart_items if item['surfboard_id'] != surfboard_id]

    session['cart'] = cart_items  # Update the cart in the session
    
    return redirect(url_for('checkout'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor() 
    
    cart_items = session.get('cart', [])
    surfboards = []
    final_total = 0

    for item in cart_items:
        cur.execute("SELECT * FROM SurfBoards WHERE surfboard_id = ?", (item['surfboard_id'],))
        surfboard = cur.fetchone()
        if surfboard:
            surfboard_dict = {
                'surfboard_id': surfboard['surfboard_id'],
                'name': surfboard['surfboard_name'],
                'type': surfboard['surfboard_type'],
                'condition': surfboard['surfboard_condtion'],
                'price': surfboard['purchase_price'],
                'image': surfboard['surfboard_photo'],
                'quantity': item['quantity']
            }
            final_total += surfboard['purchase_price'] * item['quantity']
            surfboards.append(surfboard_dict) 

    conn.close()

    return render_template('checkout.html', cart=surfboards, final_total=final_total)
@app.route('/lobby')
def lobby():
    return render_template("lobby.html")

# The entry point for running the Flask app
if __name__ == "__main__":
    app.run(debug=True)