/*global $, jQuery, ajaxSecurity*/
function activateVoting() {
    $('[data-toggle="tooltip"]').tooltip();
    $(".expand").click(function (event) {
        event.preventDefault();
        var objectUuid = $(this).data('object_uuid');
        $("#" + objectUuid + "-expandable").toggle();
    });
    $(".vote_object-action").click(function (event) {
        event.preventDefault();
        var objectUuid = $(this).data('object_uuid');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "PUT",
            url: "/v1/counsel/" + objectUuid,
            data: JSON.stringify({
                "counsel_vote_type": $(this).data("vote_type"),
                "reason": $("#" + objectUuid + "-response").val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                console.log(data);
                $.notify("Goals successfully created!", {type: 'success'});
            },
            error: function (XMLHttpRequest) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
}
$(document).ready(function () {
    "use strict";
    activateVoting();
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/counsel/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            for (var i = 0; i < data.results.length; i++) {
                $("#flag-voting-wrapper").append(data.results[i].html);
            }
            activateVoting();
            //$.notify("Updated next goal set!", {type: 'success'});
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            errorDisplay(XMLHttpRequest);
        }
    });

});
