var request = require('api').request,
    templates = require('template_build/templates'),
    settings = require('settings').settings;

export function populateMissions(loadElement, questID){
    request.get({url: '/v1/quests/' + questID + '/missions/'})
        .done(function (data) {
            if(data.results.length === 0) {
                loadElement.innerHTML = templates.position_holder({static_url: settings.static_url});
            } else {
                for(var i=0; i < data.results.length; i++){
                    data.results[i].title = determineTitle(data.results[i]);
                }
                loadElement.innerHTML = templates.mission_summary({missions: data.results, static_url: settings.static_url});
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
