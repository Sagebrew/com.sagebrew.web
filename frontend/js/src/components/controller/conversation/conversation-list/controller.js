var request = require('api').request,
    helpers = require('common/helpers'),
    Handlebars = require('handlebars'),
    questionSummaryTemplate = require('./templates/question_summary.hbs');


/**
 * Meta.
 */
export const meta = {
    controller: "conversation/conversation-list",
    match_method: "path",
    check: "^conversations$"
};


/**
 * Load
 */
export function load() {
var $app = $(".app-sb");
    Handlebars.registerPartial('question_summary', questionSummaryTemplate);

    $app
        .on('click', '.js-sort-filter', function (event) {
            event.preventDefault();

            if(!this.parentNode.classList.contains("active")){
                document.getElementById('js-conversation-list').innerHTML = '<div id="js-conversation-container"></div><div class="loader"></div>';
                var sortFilterList = document.getElementById('js-sort-filter');
                for (var i = 0; i < sortFilterList.childNodes.length; i++) {
                    if (sortFilterList.childNodes[i].className === "active"){
                        sortFilterList.childNodes[i].classList.remove("active");
                    }
                }
                this.parentNode.classList.add("active");
                loadConversations(this.dataset.ordering);
            }
        });
    loadConversations("-created");
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}

function loadConversations(sortFilter) {
    var $conversationList = $('#js-conversation-list'),
        $conversationContainer = $('#js-conversation-container');
    $conversationList.sb_contentLoader({
        emptyDataMessage: 'Start a Conversation Today :)',
        url: '/v1/questions/',
        params: {
            ordering: sortFilter,
            expand: true
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
            $conversationContainer.append(questionSummaryTemplate({conversations: data.results}));
        }
    });
}