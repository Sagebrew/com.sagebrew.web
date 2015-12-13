/*global $, enableContentFunctionality, populateComment*/
var request = require('api').request;

require('plugin/contentloader');

function loadSingleContent() {
    var wrapper = $("#js-content-wrapper"),
        objectURL,
        objectType,
        formattedObjectType,
        capitalizedOjbectType,
        parsed = (window.location.href).match(/^((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?$/);
    /*
    parsed in an array of different strings which makes up the full url.
    0: fully qualified url
    1: protocol with ex. 'https:/'
    2: protocol alone ex. 'https'
    3: host ex. 'sagebrew.com'
    4: url path ex. '/posts/'
    5: file path ex. '/posts'
    6: continued path ex. '8cd02e46-9ba6-11e5-9d85-080027242395/
    7: query params ex. '?this=query_param'
    8: hash params ex. '#this-is-my-anchor'
     */
    objectURL = "/v1" + parsed[4] + parsed[6] + "?html=true";
    objectType = parsed[4].replace(/\//g, '');
    formattedObjectType = objectType.slice(0, -1);
    capitalizedOjbectType = formattedObjectType.charAt(0).toUpperCase() + formattedObjectType.slice(1);
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
            if (data.results.to_be_deleted) {
                wrapper.append("<h1>Sorry this " + capitalizedOjbectType + " has been removed by the owner!</h1>");
                if (formattedObjectType === "solution" || formattedObjectType === "question") {
                    wrapper.append('<small><a href="' + data.results.url + '">You can still view the whole Conversation here.</a></small>');
                }
            } else {
                wrapper.prepend('<h1>' + capitalizedOjbectType + '</h1>');
                if (formattedObjectType === "solution" || formattedObjectType === "question") {
                    wrapper.append('<small><a href="' + data.results.url + '">View the full Conversation</a></small>');
                }
                wrapper.append(data.html);
                enableContentFunctionality(data.id, formattedObjectType);
                populateComment(data.id, objectType);
            }

        }
    });
}


export function init() {
    loadSingleContent();
}