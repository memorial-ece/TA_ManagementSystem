function validateForm() {
    let username = document.forms["loginForm"]["username"].value;
    let pwd = document.forms["loginForm"]["password"].value;
    if(username === ""){
        document.getElementById("invalid1").innerHTML = "username or password can't be empty";
        return false;
    }
    else if (pwd === "") {
        document.getElementById("invalid2").innerHTML = "username or password can't be empty";
        return false;
    }
}