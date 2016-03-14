var request = require('api').request,
    settings = require('settings').settings,
    getArgs = require('common/helpers').getQueryParam,
    moment = require('moment'),
    emptySearchTemplate = require('../templates/search_empty.hbs'),
    questionSearchTemplate = require('../templates/question_search.hbs'),
    profileSearchTemplate = require('../templates/user_search.hbs'),
    questSearchTemplate = require('../templates/quest_search.hbs'),
    missionSearchTemplate = require('../templates/mission_search.hbs');


export function submitSearch() {
    var searchResults = document.getElementById("search_result_div");
    searchResults.innerHTML = searchResults.innerHTML + '<div class="loader"></div>';
    request.get({url: "/v1/search/?query=" + getArgs('q') + "&filter=" + getArgs('filter')})
        .done(function (data) {
            $(".loader").remove();
            if (data.results.length === 0) {
                searchResults.innerHTML += emptySearchTemplate();
            }
            $.each(data.results, function(index, value) {
                var source = value._source;
                if (value._type === 'question') {
                    source.created = moment.parseZone(value._source.created).fromNow();
                    source.last_edited_on = moment.parseZone(value._source.last_edited_on).fromNow();
                    source.current_username = settings.user.username;
                    searchResults.innerHTML += questionSearchTemplate(value._source);
                } else if (value._type === 'profile') {
                    source.current_username = settings.user.username;
                    searchResults.innerHTML += profileSearchTemplate(source);
                } else if (value._type === 'campaign' || value._type === 'politicalcampaign' || value._type === "quest") {
                    if (!source.title) {
                        source.title = source.first_name + " " + source.last_name;
                    }
                    searchResults.innerHTML += questSearchTemplate(value._source);
                } else if (value._type === 'mission') {
                    if (!source.profile_pic) {
                        source.profile_pic = source.quest.profile_pic;
                    }
                    if (!source.quest.title) {
                        source.quest.title = source.quest.first_name + " " + source.quest.last_name;
                    }
                    searchResults.innerHTML += missionSearchTemplate(value._source);
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


