var request = require('api').request,
    positionHolderTemplate = require('controller/mission/political-mission/templates/position_holder.hbs'),
    missionSummaryTemplate = require('controller/quest/quest-view/templates/mission_summary.hbs'),
    settings = require('settings').settings;

export function populateMissions(loadElement, questID, template, emptyMessage){
    require('common/handlebars_helpers');
    require('plugin/contentloader');
    if(emptyMessage === undefined || emptyMessage === "undefined" || emptyMessage === null){
        emptyMessage = positionHolderTemplate({static_url: settings.static_url});
    }
    if(template === undefined || template === "undefined" || template === null){
        template = missionSummaryTemplate;
    }
    if(loadElement === undefined || loadElement === "undefined" || loadElement === null) {
        loadElement = $(".app-sb");
    }
    loadElement.sb_contentLoader({
        emptyDataMessage: emptyMessage,
        url: '/v1/quests/' + questID + '/missions/',
        loadingMoreItemsMessage: " ",
        itemsPerPage: 3,
        loadMoreMessage: " ",
        dataCallback: function(base_url, params) {
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
        renderCallback: function($container, data) {
            for(var i=0; i < data.results.length; i++){
                data.results[i].title = determineTitle(data.results[i]);
            }
            $container.append(template({
                missions: data.results,
                static_url: settings.static_url
            }));
        }
    });
}

export function populateEndorsements(loadElement, questID, template, emptyMessage, endorserType){
    require('common/handlebars_helpers');
    require('plugin/contentloader');
    if(emptyMessage === undefined || emptyMessage === "undefined" || emptyMessage === null){
        emptyMessage = positionHolderTemplate({static_url: settings.static_url});
    }
    if(template === undefined || template === "undefined" || template === null){
        template = missionSummaryTemplate;
    }
    if(loadElement === undefined || loadElement === "undefined" || loadElement === null) {
        loadElement = $(".app-sb");
    }
    if(endorserType === undefined || endorserType === "undefined" || endorserType === null) {
        endorserType = "profiles";
    }
    loadElement.sb_contentLoader({
        emptyDataMessage: emptyMessage,
        url: '/v1/' + endorserType + '/' + questID + '/endorsed/',
        loadingMoreItemsMessage: " ",
        itemsPerPage: 3,
        loadMoreMessage: " ",
        dataCallback: function(base_url, params) {
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
        renderCallback: function($container, data) {
            for(var i=0; i < data.results.length; i++){
                data.results[i].title = determineTitle(data.results[i]);
            }
            $container.append(template({
                missions: data.results,
                static_url: settings.static_url
            }));
        }
    });
}

export function determineTitle(mission) {
    var title;
    if (mission.focus_on_type === "position"){
        if (mission.focused_on.full_name ) {
            title = mission.focused_on.full_name;
        } else {
            title = mission.focus_name_formatted;
        }
    } else {
        if (mission.title) {
            title = mission.title;
        } else {
            title = mission.focus_name_formatted;
        }
    }
    title = title.replace('-', ' ');
    return title.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});

}
