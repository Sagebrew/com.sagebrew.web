/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/me/donations/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            console.log(data);
            $("#donation_wrapper").append(data.results);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            errorDisplay(XMLHttpRequest);
        }
    });
});