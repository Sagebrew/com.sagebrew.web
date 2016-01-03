var request = require('api').request,
    templates = require('template_build/templates'),
    settings = require('settings').settings;

export function populateMissions(loadElement, questID){
    var title;
    request.get({url: '/v1/quests/' + questID + '/missions/'})
        .done(function (data) {
            if(data.results.length === 0) {
                loadElement.innerHTML = templates.position_holder({static_url: settings.static_url});
            } else {
                for(var i=0; i < data.results.length; i++){
                    if (data.results[i].focus_on_type == "position"){
                        if (data.results[i].focused_on.full_name ) {
                            title = data.results[i].focused_on.full_name
                        } else {
                            title = data.results[i].focus_name_formatted
                        }
                    } else {
                        if (data.results[i].title) {
                            title = data.results[i].title
                        } else {
                            title = data.results[i].focus_name_formatted
                        }
                    }
                    title = title.replace('-', ' ');
                    data.results[i].title = title.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
                }
                loadElement.innerHTML = templates.mission_summary({missions: data.results, static_url: settings.static_url});
            }
        });
}