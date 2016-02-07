var helpers = require('common/helpers'),
    request = require('api').request,
    templates = require('template_build/templates');

export const meta = {
    controller: "volunteer",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/volunteer\/option"
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
    var $selectAllList = $('#js-option-list');

    request.get({url:"/v1/volunteers/options/"})
        .done(function (data) {
            $selectAllList.append(templates.volunteer_selector({options: data}));
            selectAllFields();
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}


function selectAllFields() {
    // TODO mostly duplicate from interests controller
    /**
     * This is the function that selects all the fields and deselects all the
     * fields. It works even if fields are already selected or unselected.
     * It also assigns the value to the checkbox of true or false with the
     * end dot notation of .val(!ch).
     */
    $('.toggle-all :checkbox').on('click', function () {
        var $this = $(this);
        var ch = $this.prop('checked');
        $('#js-select-all').find(':checkbox').radiocheck(!ch ? 'uncheck' : 'check');
    });
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