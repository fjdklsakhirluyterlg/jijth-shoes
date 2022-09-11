$.ajax({
    url: '/api/add/category',
    dataType: 'json',
    type: 'post',
    contentType: 'application/json',
    data: JSON.stringify( { name : $("#name").val(), items : $("#stock").val() } ),
    processData: false,
    success: function( data, textStatus, jQxhr ){
        $('#response pre').html( JSON.stringify( data ) );
    },
    error: function( jqXhr, textStatus, errorThrown ){
        console.log( errorThrown );
    }
});