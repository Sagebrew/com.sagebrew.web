var request = require('api').request,
    helpers = require('common/helpers'),
    validators = require('common/validators');

export const meta = {
    controller: "mission/mission-manage/general",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/general"
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
        })
        .on('keyup', '#about', function(){
            var $this = $(this),
                count = $this.val().length,
                remaining = $("#js-about-char-count"),
                newCount = 255 - count;
            if (newCount < 0) {
                newCount = 0;
            }
            remaining.text(newCount + " Characters Remaining");
        });
    validators.missionManageValidator($("#socialForm"));
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}