$(document).ready(function () {
    var username = $("#user_info").data("page_user_username");
    // These ajax calls are sequential due to the order which the html returned
    // are displayed on the page, we figure that if one higher up the chain
    // fails the page will look bad anyway, this ensure that if they are
    // successful the page loads correctly
    $.ajax({
        xhrFields: {withCredentials: true},
        type: 'GET',
        url: '/v1/profiles/' + username + '/president/?html=true',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function (data) {
            $("#president_wrapper").append(data);
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/profiles/" + username + "/senators/?html=true",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    $("#senator_wrapper").append(data);
                    $("#house_rep_wrapper").append(data['rep_html']);
                    $.ajax({
                        xhrFields: {withCredentials: true},
                        type: "GET",
                        url: "/v1/profiles/" + username + "/house_representative/?html=true",
                        contentType: "application/json; charset=utf-8",
                        dataType: "json",
                        success: function (data) {
                            $("#house_rep_wrapper").append(data);
                            $.ajax({
                                xhrFields: {withCredentials: true},
                                type: "GET",
                                url: "/v1/profiles/" + username + "/possible_senators/?html=true",
                                contentType: "application/json; charset=utf-8",
                                dataType: "json",
                                success: function (data) {
                                    $("#potential_senator_wrapper").append(data);
                                    $.ajax({
                                        xhrFields: {withCredentials: true},
                                        type: 'GET',
                                        url: '/v1/profiles/' + username + '/possible_house_representatives/?html=true',
                                        contentType: 'application/json; charset=utf-8',
                                        dataType: "json",
                                        success: function (data) {
                                            $("#potential_rep_wrapper").append(data);
                                            $.ajax({
                                                xhrFields: {withCredentials: true},
                                                type: 'GET',
                                                url: '/v1/profiles/' + username + '/possible_presidents/?html=true',
                                                contentType: 'application/json; charset=utf-8',
                                                dataType: "json",
                                                success: function (data) {
                                                    $("#potential_president_wrapper").append(data);
                                                },
                                                error: function (XMLHttpRequest, textStatus, errorThrown) {
                                                    if (XMLHttpRequest.status === 500) {
                                                        $("#server_error").show();
                                                    }
                                                }
                                            });
                                        },
                                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                                            if (XMLHttpRequest.status === 500) {
                                                $("#server_error").show();
                                            }
                                        }
                                    });
                                },
                                error: function (XMLHttpRequest, textStatus, errorThrown) {
                                    if (XMLHttpRequest.status === 500) {
                                        $("#server_error").show();
                                    }
                                }
                            });
                        },
                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                            if (XMLHttpRequest.status === 500) {
                                $("#server_error").show();
                            }
                        }
                    });
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    if(XMLHttpRequest.status === 500) {
                        $("#server_error").show();
                    }
                }
            });
        }
    });

});