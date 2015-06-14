/*global $, jQuery, loadPosts*/
$(document).ready(function () {
    "use strict";
    loadPosts("/v1/profiles/" + $('#user_info').data('page_user_username') + "/wall/render/?page_size=" + 5 + "&expand=true&expedite=true");
});
