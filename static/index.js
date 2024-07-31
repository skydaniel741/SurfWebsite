document.addEventListener("DOMContentLoaded", function() {
    var loader = document.getElementById("preloader");
    if (loader) {
        console.log("Preloader element found");
        window.addEventListener("load", function() {
            loader.style.display = "none";
        });
    }

    let listProducts = [];
    let cart = []; // lets the program understand on what it is selecting
    let iconCart = document.querySelector('.icon-cart');
    let closeCart = document.querySelector('.close');
    let body = document.querySelector('body');
    let openCart = document.querySelector('.checkout')

    // lets the event happen when clicked on the cart
    if (iconCart) iconCart.addEventListener('click', () => body.classList.toggle('showcart'));

    // event closes when clicked on close
    if (closeCart) closeCart.addEventListener('click', () => body.classList.remove('showcart'));

    if (openCart) openCart.addEventListener('click', () => body.classList('showcart'));

    // lets the javaScript connect to the route with the data tables
    fetch('/surfboards_data')
        .then(response => response.json())
        .then(data => {
            listProducts = data.map(row => ({
                id: row.id, // data tables
                name: row.name,
                type: row.type,
                condition: row.condition,
                price: row.price,
                image: row.image,
                rentalPrice: row.rentalPrice
            }));
            console.log(listProducts); // prints the data
            setUpAddToCartButtons();
        })
        .catch(error => console.error('Error fetching surfboards:', error)); // if error occurs prints message

    function setUpAddToCartButtons() { // function for clicking on cart add to cart
        document.querySelectorAll('.add-cart').forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault(); // prevent the form from submitting
                let surfboardId = this.closest('form').querySelector('input[name="surfboard_id"]').value;
                addToCart(surfboardId);
            });
        });
    }

    function addToCart(surfboardId) {
        let product = listProducts.find(p => p.id == surfboardId);
        if (!product) return; // if product not found, return
        let cartItem = cart.find(item => item.id == surfboardId);
        if (!cartItem) {
            // add product to the cart
            cart.push({ ...product, quantity: 1 });
        } else {
            // increment quantity if already in the cart
            cartItem.quantity += 1;
        }
        reloadCart();
    }

    // function to reload the cart
    function reloadCart() {
        let cartContainer = document.querySelector('.list-cart');
        if (!cartContainer) return; // if the cart container does not exist, return

        cartContainer.innerHTML = ''; // lets the count start at zero
        let totalPrice = 0;
        cart.forEach(item => {
            totalPrice += item.price * item.quantity;

            // create cart item element
            let cartItem = document.createElement('div');
            cartItem.classList.add('cart-item');
            cartItem.innerHTML = `
                <div class="image">
                    <img src="${item.image}" alt="${item.name}"> 
                </div>
                <div class="name">${item.name}</div>
                <div class="total_price">$${(item.price * item.quantity).toFixed(2)}</div>
                <div class="quantity">
                    <span class="remove"><</span>
                    <span>${item.quantity}</span>
                    <span class="add">></span>
                </div>
            `;
            cartContainer.appendChild(cartItem); // adds a new node to the system
        });

        // update total price
        let totalElement = document.querySelector('.cart .total');
        if (totalElement) totalElement.innerHTML = totalPrice.toLocaleString();

        // update cart quantity
        let quantityElement = document.querySelector('.cart .quantity');
        if (quantityElement) quantityElement.innerText = cart.reduce((sum, item) => sum + item.quantity, 0);
    }
})