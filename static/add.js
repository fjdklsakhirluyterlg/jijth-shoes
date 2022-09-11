function myFunction(id){
    var name = document.getElementById("name").value;
    var items = document.getElementById("stock").value;
    var user_id = id;
    data = {"name": name, "items": items, "user_id": user_id};
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function(){
        console.log("added")
    }
    xhttp.open()
    xhttp.send();
}