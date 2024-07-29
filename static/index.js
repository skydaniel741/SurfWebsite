document.addEventListener("DOMContentLoaded", function() {
    var loader = document.getElementById("preloader");
    if (loader) {
        console.log("Preloader element found");
        window.addEventListener("load", function() {
            loader.style.display = "none";
        });
    }

    let listProducts = [];
    let cart = []; // Lets the program understand on what it selecting
    let iconCart = document.querySelector('.icon-cart');
    let closeCart = document.querySelector('.close');
    let body = document.querySelector('body');
    // Lets the event happen when clicked on the cart
    if (iconCart) {
        iconCart.addEventListener('click', () => {
            body.classList.toggle('showcart');
        });
    } // event closes when clicked on close
    if (closeCart) {
        closeCart.addEventListener('click', () => {
            body.classList.remove('showcart');
        });
    }
    // lets the java connect to the json with the data tables
    const initApp = () => {
        fetch('/static/exported_surfboards.json')
            .then(response => response.json())
            .then(data => {
                listProducts = data.objects[0].rows.map(row => ({
                    id: row[0], // Data tables
                    name: row[1],
                    type: row[2],
                    condition: row[3],
                    price: row[4],
                    image: row[5],
                    rentalPrice: row[6]
                }));
                console.log(listProducts); // Prints the data
                setUpAddToCartButtons();
            })
            .catch(error => console.error('Error fetching surfboards:', error)); // If error occures prints message
    };
    initApp();

    function setUpAddToCartButtons() { // function for clicking on cart add to cart
        document.querySelectorAll('.add-cart').forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault(); // Prevent the form from submitting

                let form = this.closest('form');
                let surfboardId = form.querySelector('input[name="surfboard_id"]').value;

                addToCart(surfboardId);
            });
        });
    }

    function addToCart(surfboardId) {
        let product = listProducts.find(p => p.id == surfboardId);
        if (!product) return; // If product not found, return

        let cartItem = cart.find(item => item.id == surfboardId);
        if (!cartItem) {
            // Add product to the cart
            cart.push({ ...product, quantity: 1 });
        } else {
            // Increment quantity if already in the cart
            cartItem.quantity += 1;
        }
        reloadCart();
    }
        // function for reload the count to zero when reloaded
    function reloadCart() {
        let cartContainer = document.querySelector('.list-cart');
        if (!cartContainer) return; // If the cart container does not exist, return

        cartContainer.innerHTML = ''; // Lets the count start at zero
        let count = 0;
        let totalPrice = 0;
        //calculate the total price
        cart.forEach((item) => {
            totalPrice += item.price * item.quantity;  
            count += item.quantity;

            // Create cart item element
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
            cartContainer.appendChild(cartItem); //Adds a new node to the sytem
        });

        let totalElement = document.querySelector('.cart .total');
        if (totalElement) {
            totalElement.innerHTML = totalPrice.toLocaleString();
        }
        // should update the cart quantaity
        let quantityElement = document.querySelector('.cart .quantity');
        if (quantityElement) {
            quantityElement.innerText = count;
        }
    }
});