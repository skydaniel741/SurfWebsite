var loader = document.getElementById("preloader");
window.addEventListener("load",function(){
loader.style.display = "none"})


setInterval(setTime, 1000);
setTime();
function setTime(){
    var dt = newDate();
    time = dt.loLocalTimeString([],{hour:'2-digit',minute:'2-digit'});
    document.getElementById('date-time').innerHTML;
}



