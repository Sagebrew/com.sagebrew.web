var request = require('api').request,
    positionHolderTemplate = require('controller/mission/political-mission/templates/position_holder.hbs'),
    missionSummaryTemplate = require('controller/quest/quest-view/templates/mission_summary.hbs'),
    settings = require('settings').settings;

export function populateMissions(loadElement, questID){
    var $missionList = $('#js-mission-list'),
        $missionContainer = $('#js-mission-container');
    $missionList.sb_contentLoader({
        emptyDataMessage: positionHolderTemplate({static_url: settings.static_url}),
        url: '/v1/quests/' + questID + '/missions/',
        loadingMoreItemsMessage: "",
        loadMoreMessage: "",
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
            var missionLoaderPackage;
            if(settings.profile === null || settings.profile === "undefined" || settings.profile === undefined){
                missionLoaderPackage = {
                    missions: data.results,
                    static_url: settings.static_url,
                    free_account: true,
                    available_missions: false,
                    is_owner: false
                };
            } else {
                if(settings.profile.quest === null || settings.profile.quest === "undefined" || settings.profile.quest === undefined){
                    missionLoaderPackage = {
                        missions: data.results,
                        static_url: settings.static_url,
                        free_account: true,
                        available_missions: false,
                        is_owner: false
                    };
                } else {
                    missionLoaderPackage = {
                        missions: data.results,
                        static_url: settings.static_url,
                        free_account: settings.profile.quest.free_quest,
                        available_missions: settings.profile.quest.available_missions,
                        is_owner: settings.profile.quest.is_owner
                    };
                }
            }

            $missionContainer.append(missionSummaryTemplate(missionLoaderPackage));
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
