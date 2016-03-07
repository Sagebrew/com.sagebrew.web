/* global enableContentFunctionality, populateComments */
/**
 * @file
 * For posts. Posts only exist on the feed and profile pages, but
 * we're just going to include them in the entire profile for now.
 * TODO refactor and include the above globals.
 *
 */
var request = require('api').request,
    Autolinker = require('autolinker'),
    missions = require('common/missions'),
    newsTemplate = require('../templates/news.hbs'),
    missionNewsTemplate = require('../templates/mission_news.hbs'),
    questionNewsTemplate = require('../templates/question_news.hbs'),
    solutionNewsTemplate = require('../templates/solution_news.hbs'),
    vote = require('common/vote/vote').vote,
    settings = require('settings').settings,
    moment = require('moment');

require('plugin/contentloader');

/**
 * These should really be called load or something.
 */
export function init () {
    //
    // Load up the wall.
    var $appNewsfeed = $(".app-newsfeed");
    vote();
    $appNewsfeed.sb_contentLoader({
        emptyDataMessage: 'Get out there and make some news :)',
        url: '/v1/me/newsfeed/',
        params: {
            expedite: 'true',
            html: 'true'
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
            for (var i = 0; i < data.results.length; i++) {
                if (data.results[i].type === "news_article") {
                    data.results[i].published = moment(data.results[i].published).format("dddd, MMMM Do YYYY, h:mm a");
                    // Until we have all the templates in handlebars lets just keep them in the array
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
                    data.results[i].created = moment(data.results[i].created).format("dddd, MMMM Do YYYY, h:mm a");
                    // Until we have all the templates in handlebars lets just keep them in the array
                    data.results[i].html = missionNewsTemplate(data.results[i]);
                } else if (data.results[i].type === "question") {
                    if(data.results[i].profile.id === settings.profile.username){
                        data.results[i].is_owner = true;
                        data.results[i].restricted = true;
                    }
                    if(settings.profile.reputation < 100) {
                        data.results[i].has_reputation = true;
                    }
                    if(data.results[i].vote_type === true){
                        data.results[i].upvote = true;
                    } else if (data.results[i].vote_type === false){
                        data.results[i].downvote = true;
                    }
                    data.results[i].created = moment(data.results[i].created).format("dddd, MMMM Do YYYY, h:mm a");
                    data.results[i].can_comment = settings.profile.reputation >= 20;
                    data.results[i].html = questionNewsTemplate(data.results[i]);
                } else if (data.results[i].type === "solution") {
                    if(data.results[i].profile.id === settings.profile.username){
                        data.results[i].is_owner = true;
                        data.results[i].restricted = true;
                    }
                    if(settings.profile.reputation < 100) {
                        data.results[i].has_reputation = true;
                    }
                    if(data.results[i].vote_type === true){
                        data.results[i].upvote = true;
                    } else if (data.results[i].vote_type === false){
                        data.results[i].downvote = true;
                    }
                    data.results[i].created = moment(data.results[i].created).format("dddd, MMMM Do YYYY, h:mm a");
                    data.results[i].can_comment = settings.profile.reputation >= 20;
                    data.results[i].html = solutionNewsTemplate(data.results[i]);
                }
                $container.append(Autolinker.link(data.results[i].html));
                enableContentFunctionality(data.results[i].id, data.results[i].type);
                if(data.results[i].type !== "mission" && data.results[i].type !== "update" && data.results[i].type !== "news_article"){
                    populateComments([data.results[i].id], data.results[i].type + "s");
                }

            }
        }
    });

}