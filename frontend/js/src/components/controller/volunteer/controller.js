var helpers = require('common/helpers'),
    request = require('api').request,
    volunteerTemplate = require('controller/volunteer/templates/volunteer_selector.hbs');

export const meta = {
    controller: "volunteer",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/volunteer\/option"
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
    var $selectAllList = $('#js-option-list'),
        missionId = helpers.args(1),
        slug = helpers.args(2),
        greyPage = document.getElementById('sb-greyout-page'),
        volunteeredId = null;

    request.optionsMethod({url:"/v1/missions/" + missionId + "/volunteers/"})
        .done(function (data) {
            document.getElementById("select-loader").remove();
            $selectAllList.append(volunteerTemplate({
                options: data.actions.POST.activities.choices}));
            helpers.selectAllFields('#js-select-all');
            request.get({url:"/v1/missions/" + missionId + "/volunteers/me/"})
                .done(function (data) {
                    if(data.volunteered !== null) {
                        for(var i = 0; i < data.volunteered.activities.length; i++) {
                            document.getElementById(data.volunteered.activities[i]).checked = true;
                        }
                        volunteeredId = data.volunteered.id;
                    }
                });
        });

    $(".app-sb")
        .on('click', '#js-continue-btn', function () {
            greyPage.classList.remove('sb_hidden');
            var checked = helpers.getCheckedBoxes("options");
            if(volunteeredId === null){
                request.post({
                    url: "/v1/missions/" + missionId + "/volunteers/",
                    data: JSON.stringify({activities: checked})
                }).done(function () {
                    greyPage.classList.add('sb_hidden');
                    window.location.href = "/missions/" + missionId + "/" + slug + "/";
                });
            } else {
                request.patch({
                    url: "/v1/missions/" + missionId + "/volunteers/" + volunteeredId + "/",
                    data: JSON.stringify({activities: checked})
                }).done(function () {
                    greyPage.classList.add('sb_hidden');
                    window.location.href = "/missions/" + missionId + "/" + slug + "/";
                });
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
