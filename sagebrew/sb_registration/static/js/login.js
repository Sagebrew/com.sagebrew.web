$(document).ready(function(){
    $("#submit_login").on('click', function() {
        login_fxn();
    });

    $("#password_input").keyup(function(e) {
        if(e.which == 10 || e.which == 13) {
            login_fxn();
        }
    });
    $("#email_input").keyup(function(e) {
        if(e.which == 10 || e.which == 13) {
            login_fxn();
        }
    });
});

function login_fxn(){
    var next = "";
    try {
            next = getUrlParameter('next');
        }
        catch (err){
            next = ""
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
}