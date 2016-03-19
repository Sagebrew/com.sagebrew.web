/**
 * @file
 * For posts. Posts only exist on the feed and profile pages, but
 * we're just going to include them in the entire profile for now.
 *
 */
var request = require('api').request,
    Autolinker = require('autolinker'),
    missions = require('common/missions'),
    helpers = require('common/helpers'),
    newsTemplate = require('../templates/news.hbs'),
    missionNewsTemplate = require('../templates/mission_news.hbs'),
    questionNewsTemplate = require('../templates/question_news.hbs'),
    solutionNewsTemplate = require('../templates/solution_news.hbs'),
    postNewsTemplate = require('../templates/post_news.hbs'),
    updateNewsTemplate = require('../templates/update_news.hbs'),
    settings = require('settings').settings,
    moment = require('moment');


/**
 * These should really be called load or something.
 */
export function init () {
    //
    // Load up the wall.
    var $appNewsfeed = $(".app-newsfeed"),
        $app = $(".app-sb");
    console.log($appNewsfeed);
    $appNewsfeed.sb_contentLoader({
        emptyDataMessage: 'Get out there and make some news :)',
        url: '/v1/me/newsfeed/',
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
                if (data.results[i].type === "news_article") {
                    data.results[i].published = moment(data.results[i].published).format("dddd, MMMM Do YYYY, h:mm a");
                    data.results[i].html = newsTemplate(data.results[i]);
                } else if (data.results[i].type === "mission") {
                    data.results[i].title = missions.determineTitle(data.results[i]);
                    // TODO this should probably be done in the backend and saved off since it's just repeated all the time
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
                    data.results[i].html = missionNewsTemplate(data.results[i]);
                } else if (data.results[i].type === "question") {
                    data.results[i].html = questionNewsTemplate(data.results[i]);

                } else if (data.results[i].type === "solution") {
                    data.results[i].html = solutionNewsTemplate(data.results[i]);

                } else if (data.results[i].type === "post") {
                    data.results[i].html = postNewsTemplate(data.results[i]);

                } else if (data.results[i].type === "update") {
                    data.results[i].html = updateNewsTemplate(data.results[i]);

                }
                $container.append(Autolinker.link(data.results[i].html));
                $('[data-toggle="tooltip"]').tooltip();
                if(data.results[i].type !== "mission" && data.results[i].type !== "update" && data.results[i].type !== "news_article"){
                    $app.trigger("sb:populate:comments", {id: data.results[i].id, type: data.results[i].type});
                }

            }
        }
    });

}