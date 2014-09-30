$( document ).ready(function() {
	$("a.submit_signup").click(function(event){
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
                'first_name': $('.f_name').val(),
                'last_name': $('.l_name').val(),
			    'email': $('.email').val(),
                'password': $('.password').val(),
                'password2': $('.password2').val()
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                alert(data);
            }
		});
	});
});