/*global args*/
var request = require('api').request,
    settings = require('settings').settings,
    getArgs = require('common/helpers').getQueryParam,
    moment = require('moment'),
    templates = require('template_build/templates'),
    Handlebars = require('handlebars');


export function submitSearch() {
    Handlebars.registerHelper('ifCond', function (v1, operator, v2, options) {
        console.log(v1);
        console.log(v2);
        switch (operator) {
            case '==':
                return (v1 == v2) ? options.fn(this) : options.inverse(this);
            case '===':
                return (v1 === v2) ? options.fn(this) : options.inverse(this);
            case '<':
                return (v1 < v2) ? options.fn(this) : options.inverse(this);
            case '<=':
                return (v1 <= v2) ? options.fn(this) : options.inverse(this);
            case '>':
                return (v1 > v2) ? options.fn(this) : options.inverse(this);
            case '>=':
                return (v1 >= v2) ? options.fn(this) : options.inverse(this);
            case '&&':
                return (v1 && v2) ? options.fn(this) : options.inverse(this);
            case '||':
                return (v1 || v2) ? options.fn(this) : options.inverse(this);
            default:
                return options.inverse(this);
        }
    });
    var searchResults = $('#search_result_div');

    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/search/?query=" + getArgs('q') + "&filter=" + getArgs('filter'),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            console.log(data);
            $.each(data.results, function(index, value) {
                if (value._type === 'question') {
                    console.log(value);
                    value._source.created = moment.parseZone(value._source.created).fromNow();
                    value._source.last_edited_on = moment.parseZone(value._source.last_edited_on).fromNow();
                    value._source.current_username = settings.user.username;
                    console.log(value);
                    searchResults.append(templates.question_search(value._source));
                } else if (value._type === 'profile') {
                    console.log(value);
                    value._source.current_username = settings.user.username;
                    searchResults.append(templates.user_search(value._source));
                } else if (value._type === 'campaign' || value._type === 'politicalcampaign') {
                    searchResults.append(templates.quest_search(value._source));
                }
            });
        }
    });
}


