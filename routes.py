from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    abort
)
import sqlite3
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'secretkey'


# Connetion to database
def get_db_connection():
    conn = sqlite3.connect('SurfBoards.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')  # Staring screen
def layout():
    return render_template("lobby.html")


@app.route('/lobby')  # lobbys screen
def lobby():
    return render_template("lobby.html")


@app.errorhandler(404)  # Error Handler
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(500)  # Error Handler
def internal_server_error(e):
    return render_template('500.html')


# had to get it from chat gpt
def execute_query(query, args=()):
    conn = sqlite3.connect('SurfBoards.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    results = cursor.fetchall()
    conn.close()
    return results


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
# the route to connect the database
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("SurfBoards.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            #  Making the users be able to loggin with sessions
            session['loggedin'] = True
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['cart'] = []
            return redirect(url_for('surfboards'))
        else:  # Make the user able to access
            msg = 'Invalid username or password'
    return render_template("login.html", message=msg)


#  Signup section

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Input validation
        if not username.isalnum():
            msg = 'Username only contain letters and numbers'
        elif not password.isalnum():
            msg = 'Password only contain letters and numbers'
        else:
            # Check if the user already exists
            conn = sqlite3.connect("SurfBoards.db")
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
            user = cur.fetchone()
            if user:
                msg = 'Username already exists'
            else:
                hashed_password = generate_password_hash(password)
                cur.execute(
                    "INSERT INTO Users (username, password) VALUES (?, ?)",
                    (username, hashed_password))
                conn.commit()
                msg = 'Account created successfully'
            conn.close()

    return render_template("signup.html", message=msg)


# Logout Section
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("lobby"))


# Surfboard section
@app.route('/surfboard')
def surfboards():
    surfboards = execute_query("SELECT * FROM SurfBoards")
    return render_template("surfboards.html", surfboards=surfboards)


# Adds the surfboard to the add to cart section
@app.route('/<int:surfboard_id>/add_to_cart', methods=["POST", "GET"])
def add_to_cart(surfboard_id):
    surfboard = execute_query(
        "SELECT * FROM SurfBoards WHERE surfboard_id = ?",
        (surfboard_id,))
    if surfboard is None:
        abort(404)
    cart_items = session.get('cart', [])  # Personal cart items get
    item_in_cart = next(
        (item for item in cart_items if item
         ['surfboard_id'] == surfboard_id), None)
    if item_in_cart:
        item_in_cart['quantity'] += 1  # Adds the quantity
    else:
        cart_items.append({'surfboard_id': surfboard_id, 'quantity': 1})
    session['cart'] = cart_items
    return redirect(url_for('cart'))


# Brands section
@app.route('/brands')
def brands():
    brands = execute_query("SELECT *  FROM Brands")
    return render_template("brands.html", brands=brands)


# Sorting the product by brand name
@app.route('/surfboards/brand/<brand_name>')
def surfboards_by_brand(brand_name):
    surfboards = execute_query(
        "SELECT * FROM SurfBoards WHERE surfboard_name LIKE ?",
        ('%' + brand_name + '%',))
    if not surfboards:
        abort(404)
    return render_template(
            "surfboards.html",
            surfboards=surfboards,
            brand_name=brand_name)


# Cart section
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    conn = get_db_connection()  # Connection to database
    cur = conn.cursor()
    cart_items = session.get('cart', [])
    surfboards = []
    final_total = 0

    for item in cart_items:
        cur.execute("SELECT * FROM SurfBoards WHERE surfboard_id = ?",
                    (item['surfboard_id'],))
        surfboard = cur.fetchone()
        if surfboard:
            surfboard_dict = {  # Same dictonary below
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
    return render_template(
            'cart.html',
            cart=surfboards,
            final_total=final_total)


# Remove product from cart
@app.route('/<int:surfboard_id>/remove_from_cart', methods=['POST'])
def remove_from_cart(surfboard_id):
    surfboard = execute_query(
        "SELECT * FROM SurfBoards WHERE surfboard_id = ?",
        (surfboard_id,))
    if surfboard is None:  # abort if nothing
        abort(404)
    cart_items = session.get('cart', [])
    cart_items = [item for item in cart_items if item  # Removes item from cart
                  ['surfboard_id'] != surfboard_id]
    session['cart'] = cart_items
    return redirect(url_for('cart'))


# Checkout section
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    conn = get_db_connection()
    cur = conn.cursor()
    cart_items = session.get('cart', [])
    surfboards = []
    final_total = 0
    if not cart_items:  # If nothing in checkout abort
        abort(404)
    for item in cart_items:
        cur.execute("SELECT * FROM SurfBoards WHERE surfboard_id = ?",
                    (item['surfboard_id'],))
        surfboard = cur.fetchone()
        if surfboard:
            surfboard_dict = {  # Creating dictonary to display in checkout
                'surfboard_id': surfboard['surfboard_id'],
                'name': surfboard['surfboard_name'],
                'type': surfboard['surfboard_type'],
                'condition': surfboard['surfboard_condtion'],
                'price': surfboard['purchase_price'],
                'image': surfboard['surfboard_photo'],
                'quantity': item['quantity'],
                'total': surfboard['purchase_price'] * item['quantity']
            }
            final_total += surfboard['purchase_price'] * item['quantity']
            surfboards.append(surfboard_dict)  # Multiple the price by quantity

    conn.close()
    return render_template('checkout.html', purchased_items=surfboards,
                           final_total=final_total)


@app.route('/purchase_products', methods=['POST'])
def purchase_products():
    cart_items = session.get('cart', [])
    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session.get('user_id', None)
    for item in cart_items:  # if the item is in the cart
        cur.execute(
            "SELECT surfboard_name, purchase_price "
            "FROM SurfBoards WHERE surfboard_id = ?",
            (item['surfboard_id'],)
        )
        surfboard = cur.fetchone()
        if surfboard:
            surfboard_name = surfboard['surfboard_name']
            purchase_price = surfboard['purchase_price']
            quantity = item['quantity']  # Get the quantity from cart
            # Insert the purchase details
            cur.execute(
                "INSERT INTO Checkout (user_id, surfboard_id, surfboard_name, "
                "purchase_price, quantity) VALUES (?, ?, ?, ?, ?)",
                (user_id, item['surfboard_id'], surfboard_name, purchase_price,
                 quantity)
            )
    conn.commit()
    conn.close()

    # Clear the cart after purchase
    session['cart'] = []
    flash('Thank you for your purchase!')
    return redirect(url_for('cart'))


# Rental section
@app.route('/rent')
def rent():
    surfboards = execute_query("SELECT * FROM SurfBoards")
    # Chatgpt code for the date time
    today_date = date.today().isoformat()  # to procces the date today
    max_rental_date = (date.today().replace
                       (year=date.today().year + 1)).isoformat()
    return render_template(  # allows for date to be 1 years
        "rent.html",
        surfboards=surfboards,
        today_date=today_date,
        max_rental_date=max_rental_date)


# confirms to add the rental
@app.route('/confirm_rental/<int:surfboard_id>', methods=['POST'])
def confirm_rental(surfboard_id):
    conn = get_db_connection()
    cur = conn.cursor()
    user_id = session.get('user_id')
    rental_date = request.form['rental_date']
    cur.execute(
        "SELECT * FROM SurfBoards WHERE surfboard_id = ?",
        (surfboard_id,))
    surfboard = cur.fetchone()
    # If nothing
    if surfboard is None:
        abort(404)

    cur.execute(  # adds the product to rental table
        "INSERT INTO Rentals \
            (user_id, surfboard_name, rental_date) VALUES (?, ?, ?)",
        (user_id, surfboard['surfboard_name'], rental_date))
    session['rental_cart'] = []
    conn.commit()
    conn.close()
    # flashing the messages
    flash(f'Thank you for renting! Please be at Sumner Beach on {rental_date}')
    flash('Please logout if you are done!')  # displaying the message
    flash('Be at the beach between 10-4 pm to be able to rent')
    return redirect(url_for('rent'))


if __name__ == "__main__":
    app.run(debug=True)
