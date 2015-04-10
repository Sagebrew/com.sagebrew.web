$(document).ready(function(){
    $("#submit_settings").click(function(event){
        event.preventDefault();
        var username = $("#username").data("username");
        var first_name = $("#first_name").val();
        var last_name = $("#last_name").val();
        var email = $("#email").val();
        var old_password = $("#old_password").val();
        var new_password = $("#new_password").val();
        var new_password_confirm = $("#new_password_confirm");
        var street = $("#sb_primary").val();
        var street_additional = $("#sb_secondary").val();
        var city = $("#sb_city").val();
        var state = $("#sb_state").val();
        var zip = $("#sb_zip").val();
        var congressional_district = $("#id_congressional_district").val();
        var latitude = $("#id_latitude").val();
        var longitude = $("#id_longitude").val();
        var address_uuid = $("#address_uuid").data("object_uuid");
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PUT",
            url: "/v1/users/" + username + "/",
            data: JSON.stringify({
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": old_password,
                "new_password": new_password
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
            }
        });
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PUT",
            url: "/v1/address/" + address_uuid + "/",
            data: JSON.stringify({
                "street": street,
                "street_additional": street_additional,
                "city": city,
                "state": state,
                "postal_code": zip,
                "congressional_district": congressional_district,
                "latitude": latitude,
                "longitude": longitude
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
            }
        });
    })
});