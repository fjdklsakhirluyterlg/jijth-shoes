var action = 0

function item(id){
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
    const formData = new FormData();
    const photos = document.querySelector('input[type="file"][multiple]');

    fetch(`http://127.0.0.1:5040/api/uploads${action}`, {
    method: 'POST',
    body: formData,
    })
    .then(response => response.json())
    .then(result => {
    console.log('Success:', result);
    })
    .catch(error => {
    console.error('Error:', error);
    });

}