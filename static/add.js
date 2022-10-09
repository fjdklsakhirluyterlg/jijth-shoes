var action = 0

function item(){
    var name = document.getElementById("name").value;
    var stock = document.getElementById("stock").value;
    var price = document.getElementById("price").value;
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function(){
        console.log("stuff")
        document.getElementById("name").setAttribute('value', name);
        document.getElementById("stock").setAttribute('value', stock);
        document.getElementById("price").setAttribute('value', price);
        action = xhttp.responseText
    }
    xhttp.open("GET", `/views/add?name=${name}&stock=${stock}&price=${price}`)
    xhttp.send();
}

function image(){
    const form_data = new FormData()
    
}