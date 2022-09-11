$.ajax({
    url: '/api/add/category',
    dataType: 'json',
    type: 'post',
    contentType: 'application/json',
    data: JSON.stringify( { name : $("#name").val(), items : $("#stock").val() } ),
    processData: false,
    success: function( ){
        console.log( 'Success')
    },
    error: function( errorThrown ){
        console.log( errorThrown );
    }
});