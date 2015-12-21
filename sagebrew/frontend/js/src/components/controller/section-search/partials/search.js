/*global args*/
var request = require('./../../../api').request,
    settings = require('./../../../settings').settings,
    helpers = require('./../../../common/helpers');


export const meta = {
    controller: "section-search",
    match_method: "path",
    check: [
        "^search"
    ]
};


function submitSearch() {
    var searchResults = $('#search_result_div'),
        scrolled = false,
        next;

    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/search/api/?q=" + args('q') + "&page=" + args('page') + "&filter=" + args('filter'),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            console.log(data);
            if (data.next === null) {
                searchResults.append(data.html);
            } else {
                if (data.next !== 0) {
                    searchResults.append("<div class='load_next_page' style='display: none' data-next='" + data.next + " data-filter='" + args('filter') + "'></div>");
                }
                next = data.next;
                var dataList = data.html;
                $.each(dataList, function (i, item) {
                    console.log(i);
                    console.log(item);
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
                    url: "/search/api/?q=" + args('q') + "&page=" + next + "&filter=" + args('filter'),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        scrolled = false;
                        loadNextPage.spin(false);
                        loadNextPage.remove();
                        if (data.next !== 0 && data.next !== null) {
                            searchResults.append('<div class="load_next_page" style="display: none" data-next="' + data.next + ' data-filter="' + args('filter') + '"></div>');
                        }
                        searchResults.append(data.html);
                    }
                });
            }
        }
    });
}


export function init() {
    submitSearch();
}


