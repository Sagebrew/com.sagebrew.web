/**
 * @file
 * JS for the entire profile area.
 */

/**
 * @file
 * -- Contains all functionality for the profile section.
 */
var representatives = require('./partials/representatives'),
    friends = require('./partials/friends');

export function init() {
    $(document).ready(function(){

        representatives.init();
        friends.init();

        //
        // Expand post input.
        if ($("#post_input_id").length) {
            $("#post_input_id").click(function (){
                $("#sb_post_container").css("height","auto");
                $("#post_input_id").css("height", "100px").css("max-height", "800px").css("resize", "vertical");
                $("#sb_post_menu").show();
            });
        }


    });
    
    //
    // Intercom Tracking
    Intercom('trackEvent', 'visited-profile-page');
}

