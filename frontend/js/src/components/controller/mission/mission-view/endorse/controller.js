var request = require('api').request,
    getArgs = require('common/helpers').args;

export const meta = {
    controller: "mission/mission-view/endorse",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}$"
    ]
};

export function init() {

}

export function load() {
    var $app = $(".app-sb"),
        missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        slug = getArgs(2);
    $app
        .on('click', '#js-endorse', function(event) {
            event.preventDefault();
            var $this = $(this);
            $this.disabled = true;
            if ($this.hasClass("js-cancel-endorsement")){
                request.post({url: "/v1/missions/" + missionId + "/unendorse/", data:JSON.stringify({"endorse_as": "profile"})})
                    .done(function(){
                        window.location.href = "/missions/" + missionId + "/" + slug + "/";
                    });
            } else {
                request.post({url: "/v1/missions/" + missionId + "/endorse/", data:JSON.stringify({"endorse_as": "profile"})})
                    .done(function(){
                        window.location.href = "/missions/" + missionId + "/" + slug + "/";
                    });
            }
            return false;
        });
}