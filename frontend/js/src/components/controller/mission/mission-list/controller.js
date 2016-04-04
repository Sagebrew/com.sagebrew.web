var request = require('api').request,
    missions = require('common/missions'),
    settings = require('settings').settings,
    missionListBlockTemplate = require('controller/mission/mission-list/templates/mission_list_block.hbs');

export const meta = {
    controller: "mission/mission-list",
    match_method: "path",
    check: [
       "^missions$"
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
    var $affectFilter = $("#js-affect-filter");
    $affectFilter
        .on('click', '.js-affect-filter', function (event) {
            event.preventDefault();

            if(!this.parentNode.classList.contains("active")){
                document.getElementById('js-mission-list').innerHTML = '<div id="js-mission-container"></div><div class="loader"></div>';
                var affectFilterList = document.getElementById('js-affect-filter');
                for (var i = 0; i < affectFilterList.childNodes.length; i++) {
                    if (affectFilterList.childNodes[i].className === "active"){
                        affectFilterList.childNodes[i].classList.remove("active");
                    }
                }
                this.parentNode.classList.add("active");
                loadMissions(this.id);
            }
        });
    loadMissions("everyone");
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}

function loadMissions(affectsFilter) {
    require('plugin/contentloader');
    var $missionList = $('#js-mission-list'),
        $missionContainer = $('#js-mission-container');
    $missionList.sb_contentLoader({
        emptyDataMessage: 'Start your Mission Today :)',
        url: '/v1/missions/',
        params: {
            affects: affectsFilter
        },
        dataCallback: function(base_url, params) {
            var urlParams = $.param(params);
            var url;
            if (urlParams) {
                url = base_url + "?" + urlParams;
            }
            else {
                url = base_url;
            }

            return request.get({url:url});
        },
        renderCallback: function($container, data) {
            for(var i=0; i < data.results.length; i++){
                // TODO This is replicated in newsfeed, need to move it to a fxn
                data.results[i].title = missions.determineTitle(data.results[i]);
                if (data.results[i].focus_on_type === "position"){
                    if(data.results[i].quest.title !== "" && data.results[i].quest.title !== null){
                        data.results[i].title = data.results[i].quest.title + "'s mission for " + data.results[i].title;
                    } else {
                        data.results[i].title = data.results[i].quest.first_name + " " + data.results[i].quest.last_name + "'s mission for " + data.results[i].title;
                    }
                }
                if(data.results[i].wallpaper_pic === "" || data.results[i].wallpaper_pic === undefined || data.results[i].wallpaper_pic === null){
                    // This is legacy and should be handled for all new missions from March 03 16
                    data.results[i].wallpaper_pic = settings.static_url + "images/wallpaper_capitol_2.jpg";
                }
            }
            $missionContainer.append(missionListBlockTemplate({missions: data.results}));
        }
    });
}