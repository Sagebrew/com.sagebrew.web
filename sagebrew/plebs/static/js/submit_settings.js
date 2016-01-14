$(document).ready(function(){
    $("#delete_button").click(function(event){
        event.preventDefault();
        var username = $("#username").data("username");

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "DELETE",
            url: "/v1/users/" + username + "/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                window.location.href = "/logout/";
            }
        });
    });
    $("#js-cancel-button").click(function(event){
        event.preventDefault();
        window.location.href = "/";
    });

});