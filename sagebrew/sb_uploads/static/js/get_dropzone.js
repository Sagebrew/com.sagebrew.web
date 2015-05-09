$( document ).ready(function() {
    Dropzone.autoDiscover = false;
    var myDropzone = new Dropzone('div#myId', {url: "/upload/images/", autoProcessQueue: false});
    $('#add').on('click', function(event){
        event.preventDefault();
        var files = myDropzone.files;
        var myFormData = new FormData();

        $.each(files, function(i, j) {
            myFormData.append('myFile'+i, j);
        });

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/upload/images/",
            contentType: false,
            processData: false,
            dataType: "json",
            data: myFormData,
            success: function (data) {
                $(".dropzone").hide();
                $("#add").hide();
                $("#wall_app").prepend(data['html']);
                enable_post_functionality()
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 409) {
                    $("#signup_wrapper").empty();
                    $("#user_exists").show();
                } else if(XMLHttpRequest.status === 500){
                    $("#signup_wrapper").empty();
                    $("#server_error").show();
                }
            }
        });
    });
});

