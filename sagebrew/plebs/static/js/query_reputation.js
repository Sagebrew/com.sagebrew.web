$(document).ready(function () {
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/profiles/" + $("#reputation_total").data('username') + "/reputation/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var reputationTotal = $("#reputation_total"),
                reputationChange = $("#js-reputation-change"),
                reputationChangeWrapper = $(".js-reputation-change-wrapper");
            reputationTotal.append('<p id="js-change-data-container">' + data.reputation + '</p>');
            var reputationChangeTextContainer = $("#js-change-data-container");
            if (data.reputation_change > 0) {
                reputationChangeTextContainer.prepend('<p class="sb_reputation_notification_change_green">+</p>');
            } else if (data.reputation_change < 0) {
                reputationChangeTextContainer.prepend('<p class="sb_reputation_notification_change_red">-</p>');
            }
            reputationChange.append("<p>" + data.reputation_change + "</p>");
            reputationChangeWrapper.data("toggle", "tooltip");
            reputationChangeWrapper.data("placement", "top");
            reputationChangeWrapper.data("title", "last checked " + $.timeago(data.change_since));
            reputationChangeWrapper.tooltip();
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        if(XMLHttpRequest.status === 500){
            $("#server_error").show();
        }
    }
    });
});
