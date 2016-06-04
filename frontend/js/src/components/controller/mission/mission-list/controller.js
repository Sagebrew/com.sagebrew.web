var request = require('api').request,
    missions = require('common/missions'),
    settings = require('settings').settings,
    addresses = require('common/addresses'),
    missionListBlockTemplate = require('controller/mission/mission-list/templates/mission_list_block.hbs');

export const meta = {
    controller: "mission/mission-list",
    match_method: "path",
    check: [
       "^missions$"
    ],
    does_not_include: [
        "account"
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
    var $affectFilter = $("#js-affect-filter"),
        $app = $(".app-sb"),
        addressForm = document.getElementById('address'),
        addressValidationForm = addresses.setupAddress(function callback() {});
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
    $app
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            completeAddress(addressValidationForm, addressForm);
            return false;
        })
        .on('keypress', '#address input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeAddress(addressValidationForm, addressForm);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
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

function completeAddress(addressValidationForm, addressForm) {
    addressValidationForm.data('formValidation').validate();
    if(addressValidationForm.data('formValidation').isValid() === true) {
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        addresses.submitAddress(addressForm, submitAddressCallback, 
            "/v1/profiles/" + settings.profile.username + "/");
    }
}

function submitAddressCallback() {
    var greyPage = document.getElementById('sb-greyout-page');
    greyPage.classList.add('sb_hidden');
    window.location.reload();
}

function loadMissions(affectsFilter) {
    require('plugin/contentloader');
    var $missionList = $('#js-mission-list'),
        $missionContainer = $('#js-mission-container');
    $('[data-toggle="tooltip"]').tooltip();
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