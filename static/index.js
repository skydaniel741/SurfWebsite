document.addEventListener("DOMContentLoaded", function() {
    var loader = document.getElementById("preloader");
    if (loader) {
        console.log("Preloader element found");
        window.addEventListener("load", function() {
            loader.style.display = "none";
        }); } 

  


    let iconCart = document.querySelector('.icon-cart');
    let closeCart = document.querySelector('.close');
    let body = document.querySelector('body');
     if (iconCart) {
        iconCart.addEventListener('click', () => {
            body.classList.toggle('showcart');
        }); }
    if (closeCart) {
        closeCart.addEventListener('click', () => {
            body.classList.remove('showcart');
        });
    } 
});
