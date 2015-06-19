/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    $("#submit_goal").click(function (event) {
        event.preventDefault();
        var campaignId = $("#submit_goal").data('object_uuid');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/goals/",
            data: JSON.stringify({
                "title": $("#goal_title").val(),
                "summary": $("#goal_summary").val(),
                "description": $("#goal_description").val(),
                "pledged_vote_requirement": $("#goal_vote_req").val(),
                "monetary_requirement": $("#goal_monetary_req").val(),
                "total_required": $("#goal_monetary_req").val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                console.log(data);
                $("#existing_goals").append('<div class="row sb_goal_draggable" data-object_uuid="' + data.id + '" style="padding-left: 15px; padding-right: 15px; padding-bottom: 15px"><div class="block sb_goal sb_provide_goal"><div class="block"><div class="row"><div class="col-xs-12"><h6>' + data.title + '</h6><div id="' + data.id + '_monetary_requirement" class="col-xs-6">' + data.monetary_requirement + '</div><div class="col-xs-6">' + data.pledged_vote_requirement + '</div><p>' + data.summary + '</p><p>' + data.description + '</p><p>Total Required: <div id="' + data.id + '_total_required">' + data.total_required + '</p></div></div></div></div></div>');
                $.notify("Goals successfully created!", {type: 'success'});
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});
