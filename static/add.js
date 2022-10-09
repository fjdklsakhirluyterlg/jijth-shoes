var action = 0

function item(id){
    var name = document.getElementById("name").value;
    var stock = document.getElementById("stock").value;
    var price = document.getElementById("price").value;
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function(){
        document.getElementById("name").innerHTML = name;
        document.getElementById("stock").innerHTML = stock;
        document.getElementById("price").innerHTML = price;
        action = xhttp.responseText
    }
    xhttp.open("GET", `/views/add?name=${name}&stock=${stock}&price=${price}&user_id=${id}`)
    xhttp.send();
}

function image(){
    const formData = new FormData();
    const photos = document.querySelector('input[type="file"][multiple]');

    for (var i = 0; i < photos.length; i++){
        formData.append(`file${i}`, photos[i])
    }

    fetch(`http://127.0.0.1:5040/api/uploads?id=${action}`, {
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