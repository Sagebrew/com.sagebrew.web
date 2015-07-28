/*global $, jQuery*/
$(document).ready(function () {
    "use strict";
    function sendFriendRequest(requestArea, username) {
        $(requestArea).click(function (event) {
            event.preventDefault();
            var sendRequest = $(this);
            sendRequest.attr("disabled", "disabled");

            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/relationships/create_friend_request/",
                data: JSON.stringify({
                    'from_username': $(this).data('from_username'),
                    'to_username': $(this).data('to_username')
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    if (data.action === true) {
                        sendRequest.hide();
                        $("#js-friend-request-sent_" + username).show();
                    }
                },
                error: function (XMLHttpRequest) {
                    sendRequest.removeAttr("disabled");
                    errorDisplay(XMLHttpRequest);
                }
            });
        });
    }
    var searchResults = $('#search_result_div'),
        searchId = $('#search_param'),
        searchParam = searchId.data('search_param'),
        searchPage = searchId.data('search_page'),
        filter = searchId.data('filter'),
        scrolled = false;
    if (filter === 'undefined') {
        filter = "";
    }

    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/search/api/?q=" + searchParam + "&page=" + searchPage + "&filter=" + filter,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data.next === null) {
                searchResults.append(data.html);
            } else {
                if (data.next !== 0) {
                    searchResults.append("<div class='load_next_page' style='display: none' data-next='" + data.next + " data-filter='" + data.filter + "'></div>");
                }
                var dataList = data.html;
                $.each(dataList, function (i, item) {
                    if (item.type === 'question') {
                        var objectUUID = item.question_uuid;

                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/conversations/search/" + objectUUID + '/',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {
                                searchResults.append(data.html);
                            }
                        });
                    }
                    if (item.type === 'profile') {
                        var username = item.username;

                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/user/search/" + username + '/',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {
                                searchResults.append(data.html);
                                sendFriendRequest(".send_friend_request-action_" + username, username);
                            }
                        });
                    }
                    if (item.type === 'public_official' || item.type === 'campaign') {
                        var sagaUUID = item.object_uuid;
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/quests/" + sagaUUID + '/search',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {

                                searchResults.append(data.html);
                            }
                        });
                    }
                });
            }
        }
    });
    $(window).scroll(function () {
        if (scrolled === false) {
            if ($(window).scrollTop() + $(window).height() > ($(document).height() - $(document).height() * 0.5)) {
                scrolled = true;
                var loadNextPage = $('.load_next_page'),
                    nextPage = loadNextPage.data('next');
                loadNextPage.spin("small");
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "GET",
                    url: "/search/api/?q=" + searchParam + "&page=" + nextPage + "&filter=" + filter,
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        scrolled = false;
                        loadNextPage.spin(false);
                        loadNextPage.remove();
                        if (data.next !== 0 && data.next !== null) {
                            searchResults.append('<div class="load_next_page" style="display: none" data-next="' + data.next + ' data-filter="' + data.filter + '"></div>');
                        }
                        searchResults.append(data.html);
                    }
                });
            }
        }
    });
});



