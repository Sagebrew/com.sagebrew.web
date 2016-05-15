var request = require('api').request,
    helpers = require('common/helpers'),
    convoTopicsTemplate = require('common/templates/select_all.hbs');

export const meta = {
    controller: "registration/interests",
    match_method: "path",
    check: [
       "^registration/interests"
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
    var greyPage = document.getElementById('sb-greyout-page'),
        $selectAllList = $('#js-option-list');
    helpers.selectAllFields('#select_all_checkboxes');

    $("body").tooltip({ selector: '[data-toggle=tooltip]' });

    $(".tooltip").addClass(function () {
        if ($(this).prev().attr("data-tooltip-style")) {
            return "tooltip-" + $(this).prev().attr("data-tooltip-style");
        }
    });
    request.optionsMethod({url:"/v1/me/add_topics_of_interest/"})
        .done(function (data) {
            document.getElementById("select-loader").remove();
            $selectAllList.append(convoTopicsTemplate({
                options: data.actions.POST.interests.choices,
                select_all_statement: "I like a bit of everything"}));
            helpers.selectAllFields('#js-select-all');
            /**
            request.get({url:"/v1/me/add_topics_of_interest/"})
                .done(function (data) {
                    if(data.interests !== null) {
                        for(var i = 0; i < data.interests.length; i++) {
                            document.getElementById(data.interests[i]).checked = true;
                        }
                    }
                });
             **/
        });

    $(".app-sb")
        .on('click', '#volunteering', function () {
            $("#affiliation-js").show();
        })
        .on('click', '#attend-events', function() {
            $("#affiliation-js").show();
        })
        .on('click', '#submit-js', function(event) {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            var parties = [],
                interests = [],
                addParties = null,
                addInterests = null;

            if ($("#independent").is(':checked')) { parties.push("independent_party"); }
            if ($("#not-listed").is(':checked')) { parties.push("other"); }
            if ($("#democratic-party").is(':checked')) { parties.push("democratic_party"); }
            if ($("#republican-party").is(':checked')) { parties.push("republican_party"); }
            if ($("#libertarian-party").is(':checked')) { parties.push("libertarian_party"); }
            if ($("#green-party").is(':checked')) { parties.push("green_party"); }
            if ($("#constitution-party").is(':checked')) { parties.push("constitution_party"); }
            if ($("#volunteering").is(':checked')) { interests.push("volunteering"); }
            if ($("#attend-events").is(':checked')) { interests.push("attending_events"); }

            var interestData = JSON.stringify({
                "interests": interests
            });
            var affiliations = JSON.stringify({
               "names": parties
            });
            if(parties.length > 0){
                addParties = request.post({
                    url: "/v1/me/add_parties/",
                    data: affiliations
                });
            }
            if(interestData.length > 0){
                addInterests = request.post({
                    url: "/v1/me/add_interests/",
                    data: interestData
                });
            }
            $.when(addParties, addInterests).done(function () {
                request.post({
                    url: "/v1/me/add_topics_of_interest/",
                    data: JSON.stringify({interests: helpers.getCheckedBoxes('options')})
                }).done(function () {
                    greyPage.classList.add('sb_hidden');
                    window.location.href = "/registration/profile_picture/";
                });
            });

        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}