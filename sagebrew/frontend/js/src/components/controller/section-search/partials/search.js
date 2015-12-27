var request = require('api').request,
    settings = require('settings').settings,
    getArgs = require('common/helpers').getQueryParam,
    moment = require('moment'),
    templates = require('template_build/templates'),
    Handlebars = require('handlebars');


export function submitSearch() {
    Handlebars.registerHelper('ifCond', function (v1, operator, v2, options) {
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
    var searchResults = document.getElementById("search_result_div");
    searchResults.innerHTML = searchResults.innerHTML + '<div class="loader"></div>';
    request.get({url: "/v1/search/?query=" + getArgs('q') + "&filter=" + getArgs('filter')})
        .done(function (data) {
            $(".loader").remove();
            if (data.results.length === 0) {
                searchResults.innerHTML += templates.search_empty();
            }
            $.each(data.results, function(index, value) {
                var source = value._source;
                if (value._type === 'question') {
                    source.created = moment.parseZone(value._source.created).fromNow();
                    source.last_edited_on = moment.parseZone(value._source.last_edited_on).fromNow();
                    source.current_username = settings.user.username;
                    searchResults.innerHTML += templates.question_search(value._source);
                } else if (value._type === 'profile') {
                    source.current_username = settings.user.username;
                    searchResults.innerHTML += templates.user_search(source);
                } else if (value._type === 'campaign' || value._type === 'politicalcampaign' || value._type === "quest") {
                    if (!source.title) {
                        source.title = source.first_name + " " + source.last_name;
                    }
                    searchResults.innerHTML += templates.quest_search(value._source);
                } else if (value._type === 'mission') {
                    if (!source.profile_pic) {
                        source.profile_pic = source.quest.profile_pic;
                    }
                    if (!source.quest.title) {
                        source.quest.title = source.quest.first_name + " " + source.quest.last_name;
                    }
                    searchResults.innerHTML += templates.mission_search(value._source);
                }
            });
    });
}

export function switchSearchFilter() {
    $(".filter_button").click(function(e){
        e.preventDefault();
        var search_param = getArgs('q'),
            filter = $(this).data("filter");
        window.location.href = "/search/?q=" + search_param + "&page=1&filter=" + filter;
    });
}


