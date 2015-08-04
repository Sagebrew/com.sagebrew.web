/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    var roundId = $("#active_round").data('object_uuid');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/rounds/" + roundId + "/render_goals/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#goal_wrapper").append(data);
            //$.notify("Updated next goal set!", {type: 'success'});
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            errorDisplay(XMLHttpRequest);
        }
    });
});