/*global $, jQuery, ajaxSecurity, errorDisplay, Sortable*/
function calculateTotalRequired() {
    var selectedGoals = $("#current_goals > div.sb_goal_draggable"),
        prevGoal = null,
        totalRequired = 0;
    selectedGoals.each(function (index, value) {
        var currentId = $(this).data('object_uuid');
        if (index === 0) {
            prevGoal = null;
            totalRequired = parseInt($("#" + currentId + "_monetary_requirement").text(), 10);
        } else {
            prevGoal = $(selectedGoals[index - 1]).data('object_uuid');
            totalRequired = parseInt($("#" + prevGoal + "_total_required").text(), 10) + parseInt($("#" + currentId + "_monetary_requirement").text(), 10);
        }
        console.log(totalRequired);
        $("#" + currentId + "_total_required").text(totalRequired);
    });
}
$(document).ready(function () {

    var roundId = $("#upcoming_round").data('object_uuid');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/rounds/" + roundId + "/render_goals/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#current_goals").append(data);
            calculateTotalRequired();
            //$.notify("Updated next goal set!", {type: 'success'});
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            errorDisplay(XMLHttpRequest);
        }
    });
    Sortable.create(document.getElementById("existing_goals"), {
        group: {name: "goal_management", pull: true, put: true},
        delay: 0,
        animation: 0,
        handle: ".sb_goal_draggable",
        draggable: ".sb_goal_draggable"
    });
    Sortable.create(document.getElementById("current_goals"), {
        group: {name: "goal_management", pull: true, put: true},
        delay: 0,
        animation: 0,
        handle: ".sb_goal_draggable",
        draggable: ".sb_goal_draggable",
        onEnd: function () {
            calculateTotalRequired();
        },
        onAdd: function () {
            calculateTotalRequired();
        }
    });
    $("#toggle_create_goal").click(function (event) {
        $("#create_container").toggle();
    });
    $("#submit_round").click(function (event) {
        event.preventDefault();
        var selectedGoals = $("#current_goals > div.sb_goal_draggable"),
            prevGoal = null,
            totalRequired = 0;
        console.log(selectedGoals);
        selectedGoals.each(function (index, value) {
            var currentId = $(this).data('object_uuid');
            if (index === 0) {
                prevGoal = null;
                totalRequired = parseInt($("#" + currentId + "_monetary_requirement").text(), 10);
            } else {
                prevGoal = $(selectedGoals[index - 1]).data('object_uuid');
                totalRequired = parseInt($("#" + prevGoal + "_total_required").text(), 10) + parseInt($("#" + currentId + "_monetary_requirement").text(), 10);
            }
            console.log(totalRequired);
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/goals/" + currentId + "/",
                data: JSON.stringify({
                    "prev_goal": prevGoal,
                    "total_required": totalRequired
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    $.notify("Updated next goal set!", {type: 'success'});
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    $.ajax({
                        xhrFields: {withCredentials: true},
                        type: "PATCH",
                        url: "/v1/goals/" + currentId + "/",
                        data: JSON.stringify({
                            "prev_goal": prevGoal,
                            "total_required": totalRequired
                        }),
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data) {
                            $.notify("Updated next goal set!", {type: 'success'});
                        },
                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                            errorDisplay(XMLHttpRequest);
                        }
                    });
                }
            });
        });
    });
});