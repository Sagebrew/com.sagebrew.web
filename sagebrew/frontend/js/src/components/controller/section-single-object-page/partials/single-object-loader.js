/*global $, enableContentFunctionality, populateComment*/
var request = require('./../../../api').request,
    settings = require('./../../../settings').settings,
    helpers = require('./../../../common/helpers');

require('./../../../plugin/contentloader');


export const meta = {
    controller: "section-single-object-page",
    match_method: "path",
    check: [
        "^questions|solutions|posts|comments/([A-Za-z0-9.@_%+-]{36})"
    ]
};

function loadSingleContent() {
    var wrapper = $("#js-content-wrapper"),
        objectURL,
        objectType,
        formattedObjectType,
        parsed = (window.location.href).match(/^((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?$/);
    objectURL = "/v1" + parsed[4] + parsed[6] + "?html=true";
    objectType = parsed[4].replace(/\//g, '');
    formattedObjectType = objectType.slice(0, -1);
    wrapper.prepend('<h1>' + formattedObjectType.charAt(0).toUpperCase() + formattedObjectType.slice(1) + '</h1>');
    wrapper.sb_contentLoader({
        emptyDataMessage: "Woops! We can't find this object!",
        url: objectURL,
        params: {
            expand: 'true',
            expedite: 'true',
            html: 'true'
        },
        dataCallback: function (base_url, params) {
            var urlParams = $.param(params);
            var url;
            if (urlParams) {
                url = base_url + "?" + urlParams;
            }
            else {
                url = base_url;
            }

            return request.get({url:url});
        },
        renderCallback: function ($container, data) {
            if (formattedObjectType === "solution" || formattedObjectType === "question") {
                wrapper.append('<small><a href="' + data.results.url + '">View the full Conversation</a></small>');
            }
            wrapper.append(data.html);
            enableContentFunctionality(data.id, formattedObjectType);
            populateComment(data.id, objectType);
        }
    });
}


export function init() {
    loadSingleContent();
}