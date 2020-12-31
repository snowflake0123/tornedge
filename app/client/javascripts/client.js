//---------------------------//
// Written by Shion Tominaga //
//---------------------------//

//===================================================//
// Transfer processing when submit button is pushed. //
//===================================================//
$(function($) {
    if('ontouchstart' in window) {
        $('#btn').bind('touchstart', function(e) {
            // Prevent character selection by long tap.
            e.preventDefault();
        });
        $('#btn').bind('touchend', function(e) {
            e.preventDefault();

            // Reads form contents.
            var client_type = $('input:radio[name="type"]:checked').val();
            var receipt     = $('#receipt')[0].files[0];
            var image       = $('#image')[0].files[0];

            var formData = new FormData();
            formData.append('type', client_type);
            formData.append('receipt', receipt);
            formData.append('image', image);

            //console.log(formData);  /*** DebugCode ***/

            // POST to server.
            $.ajax({
                type:'post',
                url:'./../../server.py',
                data:formData,
                processData: false,
                contentType: false,
                dataType: 'JSON',
                scriptCharset: 'utf-8'
            }).then(
                // Success
                function(data) {
                    if(client_type == 'sender'){
                        alert(data.message);
                    }else if(client_type == 'receiver'){
                        if(data.message){
                            alert(data.message);
                        }else{
                            // Modal appears.
                            $('#modal').append('<h1>Matching Result</h1>');
                            $('#modal').append('<img src="../../' + data.imagepath + '">');
                            $('#modal').append('<p>' + data.imagename + '</p>');
                            $('#modal').append('<a class="modal-close">×</a>');

                            $('body').append('<div class="modal-overlay"></div>');
                            $('.modal-overlay').fadeIn('slow');

                            $('#modal').fadeIn('slow');

                            $('.modal-overlay, .modal-close').off().click(function(){
                                $('#modal').fadeOut('slow');
                                $('.modal-overlay').fadeOut('slow',function(){
                                    $('.modal-overlay').remove();
                                    $('#modal').empty();
                                });
                            });
                        }
                    }
                },
                // Error
                function(data) {
                    alert('[ERROR] There was a problem connecting to the server or a problem occurred while processing on the server.');
                }
            );
        });
    }
});

//=================================================//
// Display filename when images data are attached. //
//=================================================//
$(function() {
    $('#receipt').on('change', function() {
        if($('#receiptname')){$('#receiptname').remove()}
        var file = $(this).prop('files')[0];
        if(!($('.receiptname').length)){
            $('#receiptlabel').after('<div id="receiptname"></div>');
        };
        $('#receiptname').html('Receipt: ' + file.name);
    });
    $('#image').on('change', function() {
        if($('#imagename')){$('#imagename').remove()}
        var file = $(this).prop('files')[0];
        if(!($('.imagename').length)){
            $('#imglabel').after('<div id="imagename"></div>');
        };
        $('#imagename').html('Image: ' + file.name);
    });
});

//==================================================//
// Delete images data when radio button is changed. //
//==================================================//
$(function() {
    $('input[name="type"]:radio').change( function() {
        var radioval = $(this).val();
        if(radioval == 'receiver'){
            $('#receipt').replaceWith($('#receipt').clone(true));
            $('#receiptname').remove();
            $('#image').replaceWith($('#image').clone(true));
            $('#imagename').remove();

            $('#image').prop('disabled', true);
            $('#imglabel').css({'background-color':'#bdc3c7', 'color':'#869198'});
        }else{
            $('#receipt').replaceWith($('#receipt').clone(true));
            $('#receiptname').remove();

            $('#image').prop('disabled', false);
            $('#imglabel').css({'background-color':'#336699', 'color':'#FFFFFF'});
        }
    });
});
