/*global $ */
var request = require('api').request,
    helpers = require('common/helpers'),
    questionTemplate = require('controller/section-conversation/templates/question.hbs'),
    solutionTemplate = require('controller/section-conversation/templates/solution.hbs'),
    postNewsTemplate = require('controller/section-profile/templates/post_news.hbs'),
    settings = require('settings').settings,
    moment = require('moment');


function loadSingleContent() {
    var wrapper = $("#js-content-wrapper"),
        objectURL,
        objectType,
        formattedObjectType,
        capitalizedOjbectType,
        $app = $(".app-sb"),
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
    objectURL = "/v1" + parsed[4] + parsed[6] + "?expand=true";
    objectType = parsed[4].replace(/\//g, '');
    formattedObjectType = objectType.slice(0, -1);
    capitalizedOjbectType = formattedObjectType.charAt(0).toUpperCase() + formattedObjectType.slice(1);
    request.get({url: objectURL})
        .done(function (data) {
            console.log(data);
            var renderedTemplate;

            if (formattedObjectType === "solution" || formattedObjectType === "question") {
                wrapper.append('<h1 class="block-title"><a href="' + data.question.url + '"> Solution To: ' + data.question.title + ' </a></h1>');
            } else {
                wrapper.prepend('<h1 class="block-title">' + capitalizedOjbectType + '</h1>');
            }
            data = helpers.votableContentPrep([data])[0];
            if (formattedObjectType === "question") {
                renderedTemplate = questionTemplate(data);
            } else if (formattedObjectType === "solution") {
                renderedTemplate = solutionTemplate(data);
            } else if (formattedObjectType === "post") {
                renderedTemplate = postNewsTemplate(data);
            } else {
                renderedTemplate = ""
            }
            wrapper.append(Autolinker.link(renderedTemplate));
             $('[data-toggle="tooltip"]').tooltip();
            $app.trigger("sb:populate:comments", {id: data.id, type: data.type});
        })
}


export function init() {
    loadSingleContent();
}
