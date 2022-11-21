//navbar when mobile view
let menu = document.querySelector("#my_menu");
let links = document.querySelector(".my_navbar_menu");
menu.addEventListener("click", function() {
    menu.classList.toggle("is-active");
    links.classList.toggle("active");
});

//login prompt
function greet()
{
    let name = document.querySelector("#usrname").value;
    alert("Hello, " + name + "!\nCurrently, the login feature has no functions yet.\nThis website is for practice purposes only.\nTry signing up to explore more.\nThank You!");
}

//languages prompt
function my_languages()
{
    alert("Oops!, This feature is not made yet, Thank you for checking.");
}

//signup prompts
function myvalidate()
{
    let name = document.querySelector("#my_name").value;
    let mypass = document.querySelector("#pass").value;
    let newpass = document.querySelector("#re-pass").value;
    let n = mypass.length;
    if (n < 8)
    {
        alert("Password must be atleast 8 characters");
        return false;
    }
    if (mypass != newpass)
    {
        alert("Passwords do no matched.");
        return false;
    }
    alert("Hello, " + name + "!\nCurrently, the signup feature has no functions yet.\nThis website is for practice purposes only.\nTry to look around using the navbar to explore more.\nThank You!");
}

//references links in new tab
let harvard = document.querySelector("#harvard");
let w3school = document.querySelector("#w3school");
let bootstrap = document.querySelector("#bootstrap");
let edx = document.querySelector("#edx");
harvard.addEventListener("click", function() {
    window.open("https://www.harvard.edu");
});
w3school.addEventListener("click", function() {
    window.open("https://www.w3schools.com");
});
bootstrap.addEventListener("click", function() {
    window.open("https://www.getbootstrap.com/docs/4.5/getting-started/introduction/");
});
edx.addEventListener("click", function() {
    window.open("https://www.edx.org");
});


