$( document ).ready(function() {
	$("#submit_signup").click(function(event){
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/registration/signup/",
            data: JSON.stringify({
                'first_name': $('#f_name').val(),
                'last_name': $('#l_name').val(),
                'email': $('#email').val(),
                'password': $('#password').val(),
                'password2': $('#password2').val(),
                'birthday': $('#birthday').val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data, xhr) {
                console.log(data);
                if (data['detail'] === 'success'){
                    window.location.href = "/registration/signup/confirm/";
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

