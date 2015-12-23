var request = require('api').request,
    templates = require('template_build/templates'),
    settings = require('settings').settings,
    helpers = require('common/helpers');

export function load() {
    var $app = $(".app-sb"),
        missionList= document.getElementById('js-mission-list'),
        pageUser = helpers.args(1);

    request.get({url: '/v1/profiles/' + pageUser + '/missions/'})
        .done(function (data) {
            if(data.results.length === 0) {
                missionList.innerHTML = templates.position_holder({static_url: settings.static_url});
            } else {
                for(var i=0; i < data.results.length; i++){
                    data.results[i].focused_on.name = data.results[i].focused_on.name.replace('-', ' ');
                    data.results[i].focused_on.name = data.results[i].focused_on.name.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
                }
                missionList.innerHTML = templates.mission_summary({missions: data.results, static_url: settings.static_url});
            }
        });
    $app
        .on('click', '.radio-image-selector#js-donate-btn', function() {

        })
        .on('click', '.js-position', function () {
            if(this.id === "js-add-mission"){
                window.location.href = "/missions/select/";
            } else {
                window.location.href = "/missions/" + this.id + "/";
            }
        });
}
