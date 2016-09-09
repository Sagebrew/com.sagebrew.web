var locations = require('../partials/locations'),
    request = require('api').request,
    settings = require('settings').settings,
    helpers = require('common/helpers'),
    tags = require('common/tags'),
    mediumEditor = require('common/mediumeditorhelper').createMediumEditor;

/**
 * Meta.
 */
export const meta = {
    controller: "conversation/conversation-manage/create",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,70}\/manage\/conversations\/create$"
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
    var $app = $(".app-sb"),
        $secondnav = $(".navbar-secondary"),
        questionID = helpers.args(2),
        missionID = helpers.args(1),
        regExp = /\b((?:https?:(?:|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw))(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b(?!@)))/gi,
        greyPage = document.getElementById('sb-greyout-page'),
        editor = mediumEditor(".editable", "Type your Question context here");
    locations.init();
    tags.createTagSelector();
    $secondnav.on('click', '#submit', function (event) {
        event.preventDefault();
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        var $this = $(this);
        $this.attr("disabled", "disabled");
        greyPage.classList.remove('sb_hidden');
        var placeID, latitude, longitude, affected_area,
            tags = $('#sb_tag_box').val(),
            title = $('input#title_id').val(),
            serialized = editor.serialize(),
            key = Object.keys(serialized)[0],
            regexMatches = serialized[key].value.match(regExp);
        if(typeof(Storage) !== "undefined") {
            placeID = localStorage.getItem('questionPlaceID');
            latitude = localStorage.getItem('questionLatitude');
            longitude = localStorage.getItem('questionLongitude');
            affected_area = localStorage.getItem('questionAffectedArea');
        } else {
            placeID = document.getElementById('location-id').innerHTML;
            latitude = document.getElementById('location-lat').innerHTML;
            longitude = document.getElementById('location-long').innerHTML;
            affected_area = document.getElementById('location-area').innerHTML;
        }
        if (tags === "") {
            tags = [];
        }
        // Don't allow new users to submit without at least 1 url.
        if (settings.profile.privileges.indexOf("comment") > -1 || regexMatches) {
            var data = JSON.stringify({
                title: title,
                content: serialized[key].value,
                tags: tags,
                external_location_id: placeID || null,
                latitude: latitude || null,
                longitude: longitude || null,
                affected_area: affected_area || null,
                mission: missionID
            });
            request.post({url: "/v1/questions/", data: data})
                .done(function (data) {
                    window.location.href = data.url;
                })
                .fail(function () {
                    $this.removeAttr("disabled");
                    greyPage.classList.add('sb_hidden');
                });
        } else {
            $.notify({message: "Please include at least 1 url linking to information to add context or support to your question"}, {type: "danger"});
            $(this).removeAttr("disabled");
            greyPage.classList.add('sb_hidden');
        }
    })
        .on('click', '#cancel', function(event) {
            event.preventDefault();
            if(Object.prototype.toString.call(questionID) !== '[object Array]'){
                window.location.href = "/conversations/" + questionID + "/";
            } else {
                helpers.historyBackFallback("/conversations/");
            }
        });
    $app
        .on('click', '#sb_tag_box-tokenfield', function(event) {
            if (event.which === 10 || event.which === 13) {
                event.preventDefault();
                $(".submit_question-action").removeAttr("disabled");
                return false;
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