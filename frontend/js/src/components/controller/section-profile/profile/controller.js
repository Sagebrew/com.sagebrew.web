
var postcreate = require('../partials/postcreate'),
    request = require('api').request,
    settings = require('settings').settings,
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
    // Post create functionality.
    postcreate.init();
    postcreate.load();
    var missionList= document.getElementById('js-mission-list'),
        pageUser = helpers.args(1),
        endorsementList = document.getElementById('js-endorsements-list'),
        endorsementContainer = document.getElementById('js-endorsements-container'),
        $appNewsfeed = $("#js-recent-contributions"),
        $app = $(".app-sb");
    $app
        .on('click', '.js-follow', function (event) {
            event.preventDefault();
            var thisHolder = this;
            request.post({url: '/v1/profiles/' + pageUser + '/follow/'})
                .done(function () {
                    thisHolder.innerHTML = '<i class="fa fa fa-minus quest-rocket"></i> Unfollow';
                    thisHolder.classList.remove('js-follow');
                    thisHolder.classList.add('js-unfollow');
                })
        })
        .on('click', '.js-unfollow', function (event) {
            event.preventDefault();
            var thisHolder = this;
            request.post({url: '/v1/profiles/' + pageUser + '/unfollow/'})
                .done(function () {
                    thisHolder.innerHTML = '<i class="fa fa fa-plus quest-rocket"></i> Follow';
                    thisHolder.classList.add('js-follow');
                    thisHolder.classList.remove('js-unfollow');
                })
        });
    $appNewsfeed.sb_contentLoader({
        emptyDataMessage: '<div class="block"><div class="block-content">Some Public Contributions Need to Be Made</div></div>',
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


    missions.populateMissions($(missionList), pageUser, missionMinTemplate, null, '<div class="block"><div class="block-content" style="padding-bottom: 5px;"><p>Check Back Later For New Missions</p></div></div>');
    missions.populateEndorsements($(endorsementList), pageUser, missionMinTemplate, $(endorsementContainer), '<div class="block"><div class="block-content" style="padding-bottom: 5px;"><p>Check Back Later For New Endorsements</p></div></div>');
    var $appNetwork = $("#js-network-list");

    var profile_page_user = helpers.args(1);
    $appNetwork.sb_contentLoader({
        emptyDataMessage: '<div class="block"><div class="block-content" style="padding-bottom: 5px;"><p>Expand Your Base</p></div></div>',
        url: '/v1/profiles/' + profile_page_user + '/followers/',
        params: {
            expedite: 'true'
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
            $("#js-network-container").append(profilePicTemplate(data.results));
        }
    });

}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}