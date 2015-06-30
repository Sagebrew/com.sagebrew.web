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
        $(this).attr('disabled', 'disabled');
        var objectUuid = $(this).data('object_uuid'),
            voteDown = $(this).parents('div.vote_wrapper').find(".vote_down"),
            voteUp = $(this).parents('div.vote_wrapper').find(".vote_up"),
            voteType = $(this).hasClass('vote_up') ? true : false,
            buttonSelector = $(this);
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
                buttonSelector.removeAttr('disabled');
                if (voteDown.hasClass('vote_down_active') && voteType === true) {
                    voteDown.removeClass('vote_down_active');
                    voteUp.addClass('vote_up_active');
                    //upvoteCount += 2;
                } else if (voteDown.hasClass('vote_down_active') && voteType === false) {
                    voteDown.removeClass('vote_down_active');
                    //upvoteCount += 1;
                } else if (voteUp.hasClass('vote_up_active') && voteType === true) {
                    voteUp.removeClass('vote_up_active');
                    //upvoteCount -= 1;
                } else if (voteUp.hasClass('vote_up_active') && voteType === false) {
                    voteDown.addClass('vote_down_active');
                    voteUp.removeClass('vote_up_active');
                    //upvoteCount -= 2;
                } else {
                    if (voteType === true) {
                        $(this).addClass('vote_up_active');
                        //upvoteCount += 1;
                    }
                    else {
                        $(this).addClass('vote_down_active');
                        //upvoteCount -= 1;
                    }
                }
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
