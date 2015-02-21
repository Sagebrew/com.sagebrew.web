$(document).ready(function(){

    $('.submit_login').on('click', function() {
        try {
            var next = getUrlParameter('next');
        }
        catch (err){
            var next = ""
        }
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/login/api/",
            data: JSON.stringify({
                'email': $('.email').val(),
                'password': $('.password').val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                if (data['detail']==='success' && typeof next !=="undefined"){
                    window.location.href = next
                }
                else if (data['detail'] === 'success'){
                    window.location.href = data['url']
                }
                else {
                    alert(data['detail'])
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert(XMLHttpRequest.responseJSON["detail"]);
            }
        });
    });
});