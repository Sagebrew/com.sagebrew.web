$( document ).ready(function() {
    var scrolled = false;
    var data = loadPosts("/v1/profiles/" + $('#user_info').data('page_user_username') + "/wall/render/?page_size="+ 2 + "&expand=true");
    $(window).scroll(function() {
        if(scrolled == false) {
            if ($(window).scrollTop() + $(window).height() > ($(document).height() - $(document).height()*.5)) {
                scrolled = true;
                if (data['next'] !== null)
                {
                    data = loadPosts(data['next']);
                    scrolled = false;
                }
            }
        }
    });
});
