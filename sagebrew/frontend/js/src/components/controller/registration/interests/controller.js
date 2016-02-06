var request = require('api').request;

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
    selectAllFields();

    $("[data-toggle='tooltip']").tooltip('hide');

    $(".tooltip").addClass(function () {
        if ($(this).prev().attr("data-tooltip-style")) {
            return "tooltip-" + $(this).prev().attr("data-tooltip-style");
        }
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
                document.interstForm.submit();
            });

        });
}

function selectAllFields() {
    /**
     * This is the function that selects all the fields and deselects all the
     * fields. It works even if fields are already selected or unselected.
     * It also assigns the value to the checkbox of true or false with the
     * end dot notation of .val(!ch).
     */
    $('.toggle-all :checkbox').on('click', function () {
      var $this = $(this);
      var ch = $this.prop('checked');
      $('#select_all_checkboxes').find(':checkbox').radiocheck(!ch ? 'uncheck' : 'check');
    });
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();
    $('[data-toggle="checkbox"]').radiocheck();

    /**
     * Does individual checkboxes and when they are clicked assigns the value
     * associated with the checkbox input to either true or false since
     * it appears bootstrap/flat ui rely on the class of the label to change
     * between checked and a blank string rather then the actual value of the
     * input. This is needed for Django to understand what was selected not
     * for the actual view of the interface. The actual checkbox population in
     * the interface is done automatically by flat ui's js files.
     */
    $('.checkbox-toggle input').each(function (ind, item) {
        $(item).change(function () {
            var label = $("label[for='" + $(item).attr('id') + "']")[1];
            var label_class = $(label).attr('class');
            var label_last = label_class.substr(label_class.lastIndexOf(' ') + 1);

            if (label_last === "checked") {
                $(item).val(true);
            } else {
                $(item).val(false);
            }
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