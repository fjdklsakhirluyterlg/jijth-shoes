function item(){
    var name = document.getElementById("name").value;
    var stock = document.getElementById("stock").value;
    var price = document.getElementById("price").value;
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function(){
        console.log("stuff")
        alert(xhttp.responseText);
        document.getElementById("name").innerHTML = name;
        document.getElementById("stock").innerHTML = stock;
        document.getElementById("price").innerHTML = price;
        var form = document.getElementById("images");
        form.action = `/api/uploads?id=${xhttp.responseText}`
    }
    xhttp.open("GET", `/views/add?name=${name}&stock=${stock}&price=${price}`)
    xhttp.send();
}