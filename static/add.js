var action = 0

function item(id){
    var name = document.getElementById("name").value;
    var stock = document.getElementById("stock").value;
    var price = document.getElementById("price").value;
    fetch(`/views/add?name=${name}&stock=${stock}&price=${price}`).then(response => response.json())
    .then(result => {
    console.log('Success:', result);
    })
    .catch(error => {
    console.error('Error:', error);
    });
}

function image(){
    const formData = new FormData();
    const photos = document.querySelector('input[type="file"][multiple]');

    for (var i = 0; i < photos.length; i++){
        formData.append(`file`, photos.files[i])
    }
    console.log(photos.files)
    // fetch(`http://127.0.0.1:5040/api/uploads?id=${action}`, {
    // method: 'POST',
    // body: formData,
    // })
    // .then(response => response.json())
    // .then(result => {
    // console.log('Success:', result);
    // })
    // .catch(error => {
    // console.error('Error:', error);
    // });

}