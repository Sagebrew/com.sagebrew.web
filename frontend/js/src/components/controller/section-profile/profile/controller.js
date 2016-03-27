
var postcreate = require('../partials/postcreate'),
    request = require('api').request,
    Autolinker = require('autolinker'),
    missions = require('common/missions'),
    helpers = require('common/helpers'),
    questionSummaryTemplate = require('controller/conversation/conversation-list/templates/question_summary.hbs'),
    solutionSummaryTemplate = require('controller/conversation/conversation-list/templates/solution_summary.hbs'),
    profilePicTemplate = require('../templates/profile_pic.hbs'),
    missionMinTemplate = require('../templates/mission_min.hbs');

/**
 * Meta.
 */
export const meta = {
    controller: "section-profile/profile",
    match_method: "path",
    check: "^user",
    does_not_include: ["newsfeed"]
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
    require('plugin/contentloader');
    // Post create functionality.
    postcreate.init();
    postcreate.load();
    var missionList= document.getElementById('js-mission-list'),
        pageUser = helpers.args(1),
        endorsementList = document.getElementById('js-endorsements-list'),
        $followerList = $("#js-follower-list"),
        $followingList = $("#js-following-list"),
        $appNewsfeed = $("#js-recent-contributions"),
        profile_page_user = helpers.args(1),
        fileName = helpers.generateUuid(),
        wallpaperID = helpers.generateUuid(),
        $app = $(".app-sb");
    $app
        .on('click', '.js-follow', function (event) {
            event.preventDefault();
            var thisHolder = this;
            thisHolder.classList.add('disabled');
            request.post({url: '/v1/profiles/' + pageUser + '/follow/'})
                .done(function () {
                    thisHolder.innerHTML = '<i class="fa fa fa-minus quest-rocket"></i> Unfollow';
                    thisHolder.classList.remove('js-follow');
                    thisHolder.classList.add('js-unfollow');
                    thisHolder.classList.remove('disabled');
                });
        })
        .on('click', '.js-unfollow', function (event) {
            event.preventDefault();
            var thisHolder = this;
            thisHolder.classList.add('disabled');
            request.post({url: '/v1/profiles/' + pageUser + '/unfollow/'})
                .done(function () {
                    thisHolder.innerHTML = '<i class="fa fa fa-plus quest-rocket"></i> Follow';
                    thisHolder.classList.add('js-follow');
                    thisHolder.classList.remove('js-unfollow');
                    thisHolder.classList.remove('disabled');
                });
        });
    $appNewsfeed.sb_contentLoader({
        emptyDataMessage: '<div class="block"><div class="block-content five-padding-bottom">' +
        '<p>Some Public Contributions Need to Be Made</p></div></div>',
        url: '/v1/me/public/',
        params: {
            expand: 'true'
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
            data.results = helpers.votableContentPrep(data.results);
            for (var i = 0; i < data.results.length; i++) {
                if (data.results[i].type === "question") {
                    data.results[i].html = questionSummaryTemplate({conversations: [data.results[i]]});
                } else if (data.results[i].type === "solution") {
                    data.results[i].html = solutionSummaryTemplate({solutions: [data.results[i]]});
                }
                $container.append(Autolinker.link(data.results[i].html));
                $('[data-toggle="tooltip"]').tooltip();
            }
        }
    });


    missions.populateMissions($(missionList), pageUser, missionMinTemplate,
        '<div class="block"><div class="block-content five-padding-bottom">' +
        '<p class="row-no-top-bottom-margin">Check Back Later For New Missions</p></div></div>');
    missions.populateEndorsements($(endorsementList), pageUser, missionMinTemplate,
        '<div class="block"><div class="block-content five-padding-bottom">' +
        '<p class="row-no-top-bottom-margin">Check Back Later For New Endorsements</p></div></div>');

    $followerList.sb_contentLoader({
        emptyDataMessage: '<div class="block"><div class="block-content no-top-bottom-padding">' +
        '<p>Expand Your Base</p>' +
        '</div></div>',
        url: '/v1/profiles/' + profile_page_user + '/followers/',
        endingPage: 5,
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
            $container.append(profilePicTemplate({profiles: data.results}));
        }
    });
    $followingList.sb_contentLoader({
        emptyDataMessage: '<div class="block"><div class="block-content no-top-bottom-padding">' +
        '<p>Expand Your Base</p></div></div>',
        url: '/v1/profiles/' + profile_page_user + '/following/',
        endingPage: 5,
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
            $container.append(profilePicTemplate({profiles: data.results}));
        }
    });

    var croppicContainerEyecandyOptions = {
        uploadUrl: '/v1/upload/?croppic=true&random=' + fileName,
        cropUrl: '/v1/upload/' + fileName + '/crop/?resize=true&croppic=true',
        imgEyecandy: false,
        rotateControls: false,
        doubleZoomControls: false,
        zoomFactor: 100,
        onAfterImgCrop: function (arg1) {
            request.patch({
                url: "/v1/me/",
                data: JSON.stringify({"profile_pic": arg1.url}),
                cache: false,
                processData: false
            }).done(function () {
                cropContainerEyecandy.reset();
            });
        },
        onError: function (errorMsg) {
            request.errorDisplay(errorMsg)
        },
        onReset: function () {
            request.remove({
                url: "/v1/upload/" + fileName + "/",
                cache: false,
                processData: false
            });
            request.get({
                url:"/v1/me/",
                cache: false,
                processData: false
            }).done(function (data) {
                var profileImg = $("#profile_pic");
                if (profileImg.length === 0) {
                    $(".croppedImg").remove();
                    $("#cropProfilePageEyecandy").append('<img id="profile_pic" src="' + data.profile_pic + "?" + new Date().getTime() + '">');
                } else {
                    profileImg.attr('src', data.profile_pic);
                }
            })
        }
    };
    var cropContainerEyecandy = new Croppic('cropProfilePageEyecandy', croppicContainerEyecandyOptions);

    var EyecandyOptionsWallpaper = {
        uploadUrl: '/v1/upload/?croppic=true&random=' + wallpaperID,
        cropUrl: '/v1/upload/' + wallpaperID + '/crop/?resize=true&croppic=true',
        imgEyecandy: false,
        rotateControls: false,
        doubleZoomControls: false,
        zoomFactor: 100,
        onAfterImgCrop: function (arg1) {
            request.patch({
                url: "/v1/me/",
                data: JSON.stringify({"wallpaper_pic": arg1.url}),
                cache: false,
                processData: false
            }).done(function () {
                wallpaperCropContainerEyecandy.reset();
            });
        },
        onError: function (errorMsg) {
            request.errorDisplay(errorMsg)
        },
        onReset: function () {
            request.remove({
                url: "/v1/upload/" + wallpaperID + "/",
                cache: false,
                processData: false
            });
            request.get({
                url:"/v1/me/",
                cache: false,
                processData: false
            }).done(function (data) {
                var wallpaperImg = $("#wallpaper_pic");
                if (wallpaperImg.length === 0) {
                    $(".croppedImg").remove();
                    $("#cropWallpaperPictureEyecandy").append('<img id="wallpaper_pic" class="wallpaper_profile" src="' + data.wallpaper_pic + '">');
                } else {
                    wallpaperImg.attr('src', data.wallpaper_pic);
                }
            })
        }
    };
    var wallpaperCropContainerEyecandy = new Croppic('cropWallpaperPictureEyecandy', EyecandyOptionsWallpaper);
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}