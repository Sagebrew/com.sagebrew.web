var request = require('api').request,
    getArgs = require('common/helpers').args;

export const meta = {
    controller: "mission/mission-view/endorse",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/endorse$"
    ]
};

export function init() {

}

export function load() {
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        slug = getArgs(2);
    $app
        //
        // TODO repeat code as what we use in section-profile friends.js
        .on('mouseenter', ".js-hover-overlay-activate", function(event) {
            event.preventDefault();
            var $this = $(this),
            overlay = $this.parent().parent().find(".sb-overlay");
            overlay.height($this.height());
            overlay.fadeIn('fast');
        })
        //
        // Remove overlay when mouse leaves card region
        .on('mouseleave', '.sb-overlay', function(event) {
            event.preventDefault();
            $(this).fadeOut('fast');
            $(".sb-profile-not-friend-element-image").removeClass("active");
        })
        .on('click', '#js-endorse-pleb', function(event) {
            event.preventDefault();
            var $this = $(this);
            $this.disabled = true;
            if ($this.hasClass("js-cancel-endorsement")){
                request.post({url: "/v1/missions/" + missionId + "/unendorse/", data:JSON.stringify({"endorse_as": "pleb"})})
                    .done(function(){
                        window.location.href = "/missions/" + missionId + "/" + slug + "/";
                    });
            } else {
                request.post({url: "/v1/missions/" + missionId + "/endorse/", data:JSON.stringify({"endorse_as": "pleb"})})
                    .done(function(){
                        window.location.href = "/missions/" + missionId + "/" + slug + "/";
                    });
            }
        })
        .on('click', '#js-endorse-quest', function(event) {
            event.preventDefault();
            var $this = $(this);
            $this.disabled = true;
            if ($this.hasClass("js-cancel-endorsement")){
                request.post({url: "/v1/missions/" + missionId + "/unendorse/", data:JSON.stringify({"endorse_as": "quest"})})
                    .done(function(){
                        window.location.href = "/missions/" + missionId + "/" + slug + "/";
                    });
            } else {
                request.post({url: "/v1/missions/" + missionId + "/endorse/", data:JSON.stringify({"endorse_as": "quest"})})
                    .done(function(){
                        window.location.href = "/missions/" + missionId + "/" + slug + "/";
                    });
            }
        });
}