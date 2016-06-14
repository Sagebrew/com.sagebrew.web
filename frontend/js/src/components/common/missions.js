var request = require('api').request,
    positionHolderTemplate = require('controller/mission/registration/political-mission/templates/position_holder.hbs'),
    missionSummaryTemplate = require('controller/quest/quest-view/templates/mission_summaries.hbs'),
    missionShowTemplate = require('controller/mission/templates/show_more_missions.hbs'),
    settings = require('settings').settings;


export function populateMissions({loadElement, questID, template, emptyMessage,
                                 continuousLoad, additionalMissionElement, 
                                 additionalMissionWrapper, nextPage, buttonText}={}){
    require('common/handlebars_helpers');
    require('plugin/contentloader');
    if(emptyMessage === undefined || emptyMessage === "undefined" || emptyMessage === null){
        emptyMessage = positionHolderTemplate({static_url: settings.static_url});
    }
    if(template === undefined || template === "undefined" || template === null){
        template = missionSummaryTemplate;
    }
    if(continuousLoad === undefined || continuousLoad === "undefined" || continuousLoad === null) {
        continuousLoad = true;
    }
    if(loadElement === undefined || loadElement === "undefined" || loadElement === null) {
        loadElement = $(".app-sb");
    }
    if(buttonText === undefined || buttonText === "undefined" || buttonText === null) {
        buttonText = "Select";
    }
    loadElement.sb_contentLoader({
        emptyDataMessage: emptyMessage,
        url: '/v1/quests/' + questID + '/missions/',
        loadingMoreItemsMessage: " ",
        itemsPerPage: 3,
        continuousLoad: continuousLoad,
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
                // Required for legacy Quests
                if(data.results[i].level !== null) {
                    data.results[i].level = data.results[i].level.replace('_', " ").replace("-", " ");
                }
            }
            $container.append(template({
                missions: data.results,
                static_url: settings.static_url,
                button_text: buttonText
            }));
            if(continuousLoad === false) {
                if (additionalMissionElement !== null && data.next === null) {
                    additionalMissionWrapper.remove();
                } else {
                    additionalMissionWrapper.remove();
                    loadElement.append(
                        missionShowTemplate({page: nextPage, show: "mission"}));
                }
            }
        }
    });
}

export function populateEndorsements(loadElement, questID, template, emptyMessage, endorserType,
                                    continuousLoad, additionalEndorsementElement,
                                    additionalEndorsementWrapper, nextPage, buttonText){
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
    if(continuousLoad === undefined || continuousLoad === "undefined" || continuousLoad === null) {
        continuousLoad = true;
    }
    if(endorserType === undefined || endorserType === "undefined" || endorserType === null) {
        endorserType = "profiles";
    }
    if(buttonText === undefined || buttonText === "undefined" || buttonText === null) {
        buttonText = "View";
    }
    loadElement.sb_contentLoader({
        emptyDataMessage: emptyMessage,
        url: '/v1/' + endorserType + '/' + questID + '/endorsed/',
        loadingMoreItemsMessage: " ",
        itemsPerPage: 3,
        continuousLoad: continuousLoad,
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
                data.results[i].level = data.results[i].level.replace('_', " ").replace("-", " ");
            }
            $container.append(template({
                missions: data.results,
                static_url: settings.static_url,
                button_text: buttonText
            }));
            if(continuousLoad === false) {
                if (additionalEndorsementElement !== null && data.next === null) {
                    additionalEndorsementWrapper.remove();
                } else {
                    additionalEndorsementWrapper.remove();
                    loadElement.append(
                        missionShowTemplate({page: nextPage, show: "endorsement"}));
                }
            }
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
