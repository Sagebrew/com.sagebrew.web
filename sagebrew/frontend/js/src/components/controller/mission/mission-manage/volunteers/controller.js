var request = require('api').request,
    templates = require('template_build/templates'),
    humanize = require('common/helpers').humanizeString;

export const meta = {
    controller: "mission/mission-manage/volunteers",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/volunteers$"
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
    var missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $volunteerWrapper = $("#js-list-volunteer-tables"),
        $app = $(".app-sb");
    request.get({url: "/v1/missions/" + missionId + "/volunteers/expanded_data/"})
        .done(function (data) {
            for (var volunteerType in data) {
                $volunteerWrapper.append(templates.volunteer_table({
                    volunteer: data[volunteerType],
                    block_name: humanize(volunteerType)
                }));
            }
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}