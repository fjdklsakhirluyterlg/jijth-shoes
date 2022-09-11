function myFunction(){
    var name = document.getElementById("name").value;
    var stock = document.getElementById("stock").value;
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function(){
        console.log("stuff")
    }
    xhttp.open("GET", `/views/add?name=${name}&stock=${stock}`, true)
    xhttp.send();
}