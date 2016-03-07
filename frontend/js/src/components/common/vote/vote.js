var Handlebars = require('handlebars'),
    request = require('api').request,
    votingTemplate = require('common/vote/templates/vote.hbs');


export function vote() {
    Handlebars.registerPartial('vote', votingTemplate);
    var $app = $(".app-sb"),
        voteBackup;
    $app
        .on('click', '.js-vote-up', function () {
            var voteDown = $(this).parents('div.vote-wrapper').find(".js-vote-down"),
                voteCountElem = $(this).parents('div.vote-wrapper').find(".vote_count_wrapper").find('.vote_count'),
                voteCount = parseInt(voteCountElem.text(), 10),
                voteUp = $(this);
            if (voteUp.hasClass('is_owner')) {
                $.notify({message: "You cannot vote on your own Conversation Cloud Content"}, {type: 'info'});
            } else {
                voteUp.attr("disabled", "disabled");
                if (voteUp.hasClass('vote_up_active')) {
                    voteUp.removeClass('vote_up_active');
                    voteCount -= 1;
                    voteBackup = -1;
                } else {
                    if(voteDown.hasClass('vote_down_active')){
                        voteDown.removeClass('vote_down_active');
                        voteUp.addClass('vote_up_active');
                        voteCount += 2;
                        voteBackup = 2;
                    } else {
                        voteUp.addClass('vote_up_active');
                        voteCount += 1;
                        voteBackup = 3;
                    }

                }
                request.post({
                    url: "/v1/" + this.dataset.parent_type + "s/" + this.dataset.parent_id + "/votes/?expedite=true",
                    data: JSON.stringify({'vote_type': true})
                }).done(function() {
                    voteUp.removeAttr("disabled");
                    voteCountElem.text(voteCount);
                }).fail(function () {
                    voteUp.removeAttr("disabled");
                    backupVotes(voteUp, voteDown, voteBackup);
                });
            }

        })
        .on('click', '.js-vote-down', function () {
            var voteUp = $(this).parents('div.vote-wrapper').find(".js-vote-up"),
                voteCountElem = $(this).parents('div.vote-wrapper').find(".vote_count_wrapper").find('.vote_count'),
                voteCount = parseInt(voteCountElem.text(), 10),
                voteDown = $(this);
            if (this.classList.contains('is_owner')) {
                $.notify({message: "You cannot vote on your own Conversation Cloud Content"}, {type: 'info'});
            } else if(this.classList.contains('js-needs-rep')){
                $.notify({message: "You must have 100+ Reputation to Downvote"}, {type: 'info'});
            } else {
                voteDown.attr("disabled", "disabled");
                if (voteDown.hasClass('vote_down_active')) {
                    voteDown.removeClass('vote_down_active');
                    voteCount += 1;
                     voteBackup = 1;
                } else {
                    if(voteUp.hasClass('vote_up_active')){
                        voteUp.removeClass('vote_up_active');
                        voteDown.addClass('vote_down_active');
                        voteCount -= 2;
                        voteBackup = -2;
                    } else {
                        voteDown.addClass('vote_down_active');
                        voteCount -= 1;
                        voteBackup = -3;
                    }
                }
                request.post({
                    url: "/v1/" + this.dataset.parent_type + "s/" + this.dataset.parent_id + "/votes/?expedite=true",
                    data: JSON.stringify({'vote_type': false})
                }).done(function() {
                    voteDown.removeAttr("disabled");
                    voteCountElem.text(voteCount);
                }).fail(function () {
                    voteDown.removeAttr("disabled");
                    backupVotes(voteUp, $(this), voteBackup);
                });
            }
        });
}


function backupVotes(voteUp, voteDown, voteBackup) {
    if(voteBackup === 2 || voteBackup === 1){
        voteDown.addClass('vote_down_active');
        voteUp.removeClass('vote_up_active');
    } else if(voteBackup === -1 || voteBackup === -2){
        voteUp.addClass('vote_up_active');
        voteDown.removeClass('vote_down_active');
    } else if(voteBackup === 3) {
        voteUp.removeClass('vote_up_active');
    } else if(voteBackup === -3) {
        voteDown.removeClass('vote_down_active');
    }
}