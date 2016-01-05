var templates = require('template_build/templates'),
    helpers = require('common/helpers'),
    settings = require('settings').settings,
    charts = require('./partials/charts');

export const meta = {
    controller: "quest/quest-insights",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/insights"
    ]
};


/**
 * Init
 */
export function init() {

}

/**
 * Load
 */

export function load() {
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0];
    $app
        .on('click', '#submit', function(event) {
            event.preventDefault();
            var data = helpers.getFormData(document.getElementById('socialForm'));
            request.patch({url: "/v1/missions/" + missionId + "/",
                data: JSON.stringify(data)
            }).done(function (){
                $.notify({message: "Updated Settings Successfully"}, {type: "success"});
            });
        });
    charts.getCharts();
}