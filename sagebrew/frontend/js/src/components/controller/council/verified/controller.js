var request = require('api').request,
    templates = require('template_build/templates'),
    moment = require('moment');


export const meta = {
    controller: "council/verified",
    match_method: "path",
    check: [
        "^council\/positions\/verified$"
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
    var positionWrapper = $("#js-position-verification-wrapper");
    request.get({url: "/v1/positions/user_created/"})
        .done(function(data){
            positionWrapper.append(templates.verified_positions({positions:data}));
            $(".position-created").each(function(){
                var $this = $(this),
                    momentTime = moment($this.html()).format("dddd, MMMM Do YYYY, h:mm a");
                $this.html(momentTime);
            });
            $('[data-toggle="tooltip"]').tooltip();
            $(".js-verify-position").on('click', function(event){
                event.preventDefault();
                var $this = $(this);
                request.patch({url: "/v1/positions/" + $(this).data('object_uuid') + "/council_update/", data: JSON.stringify({"verified": false})})
                    .done(function(){
                        $this.closest('tr').remove();
                    });
            });
        });

}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}