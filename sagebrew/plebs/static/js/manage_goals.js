/*global $, jQuery, ajaxSecurity, errorDisplay, Sortable*/
Number.prototype.format = function (n, x) {
    var re = '\\d(?=(\\d{' + (x || 3) + '})+' + (n > 0 ? '\\.' : '$') + ')';
    return this.toFixed(Math.max(0, ~~n)).replace(new RegExp(re, 'g'), '$&,');
};

function calculateTotalRequired() {
    var selectedGoals = $("#current_goals > div.sb_goal_draggable"),
        prevGoal = null,
        totalRequired = 0;
    selectedGoals.each(function (index, value) {
        var currentId = $(this).data('object_uuid');
        if (index === 0) {
            prevGoal = null;
            totalRequired = parseInt($("#" + currentId + "_monetary_requirement").data("monetary_requirement"), 10);
        } else {
            prevGoal = $(selectedGoals[index - 1]).data('object_uuid');
            totalRequired = parseInt($("#" + prevGoal + "_required").attr("data-total_required"), 10) + parseInt($("#" + currentId + "_monetary_requirement").attr("data-monetary_requirement"), 10);
        }
        $("#" + currentId + "_required").attr("data-total_required", totalRequired);
        $("#" + currentId + "_required").text("$" + (totalRequired / 100).format());
    });
}

function submitGoal(currentId, goalData) {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "PATCH",
        url: "/v1/goals/" + currentId + "/",
        data: JSON.stringify(goalData),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            submitGoal(currentId, goalData)
        }
    });
}

$(document).ready(function () {
    var roundId = $("#upcoming_round").data('object_uuid'),
        campaignId = $("#campaign_id").data('object_uuid');
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/campaigns/" + campaignId + "/unassigned_goals/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#existing_goals").append(data);
            calculateTotalRequired();
            //$.notify("Updated next goal set!", {type: 'success'});
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            errorDisplay(XMLHttpRequest);
        }
    });
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
        onSort: function () {
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
            totalRequired = 0,
            unSelectedGoals = $("#existing_goals > div.sb_goal_draggable");
        unSelectedGoals.each(function (index, value) {
            var currentId = $(this).data('object_uuid'),
                goalData = {
                    "totalRequired": $("#" + currentId + "_monetary_requirement").attr("data-monetary_requirement")
                };
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/goals/" + currentId + "/disconnect_round/",
                data: JSON.stringify(goalData),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    console.log(data);
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    submitGoal(goalData);
                }
            });
        });
        selectedGoals.each(function (index, value) {
            var currentId = $(this).data('object_uuid');
            if (index === 0) {
                prevGoal = null;
                totalRequired = parseInt($("#" + currentId + "_monetary_requirement").attr("data-monetary_requirement"), 10);
            } else {
                prevGoal = $(selectedGoals[index - 1]).data('object_uuid');
                totalRequired = parseInt($("#" + prevGoal + "_required").attr("data-total_required"), 10) + parseInt($("#" + currentId + "_monetary_requirement").attr("data-monetary_requirement"), 10);
            }
            $("#" + currentId + "_required").attr('data-total_required', totalRequired);
            $("#" + currentId + "_required").text("$" + (totalRequired / 100).format());
            var goalData = {
                "prev_goal": prevGoal,
                "total_required": totalRequired,
                "campaign": campaignId
            };
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "PATCH",
                url: "/v1/goals/" + currentId + "/",
                data: JSON.stringify(goalData),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    submitGoal(goalData);
                }
            });
        });
        $.notify("Updated next goal set!", {type: 'success'});
    });
});