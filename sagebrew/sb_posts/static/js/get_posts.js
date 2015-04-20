$( document ).ready(function() {
    loadPosts("/v1/profiles/" + $('#user_info').data('page_user_username') + "/wall/render/?page_size="+ 2 + "&expand=true");
});
