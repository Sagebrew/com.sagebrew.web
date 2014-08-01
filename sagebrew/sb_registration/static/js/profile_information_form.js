$(document).ready(function () {
    // jQuery UI Datepicker
    var datepickerSelector = '#datepicker-01';
    $(datepickerSelector).datepicker({
        showOtherMonths: true,
        selectOtherMonths: true,
        dateFormat: "mm/dd/yy",
        changeYear: true,
        yearRange: '-100:+0'
    }).prev('.btn').on('click', function (e) {
        e && e.preventDefault();
        $(datepickerSelector).focus();
    });
    $.extend($.datepicker, {_checkOffset: function (inst, offset, isFixed) {
        return offset
    }});

    // Now let's align datepicker with the prepend button
    $(datepickerSelector).datepicker('widget').css({'margin-left': -$(datepickerSelector).prev('.input-group-btn').find('.btn').outerWidth()});

    // Commented out because switching back to a Text field for input. Believe it flows better and improves the look
    // and feel of the site. This is here as a reminder that we can use JQuery from Flat UI's application.js
    // file to implement selectors and other UI elements.
    // $("#id_state").selectpicker({style: 'btn-hg btn-primary', menuStyle: 'dropdown-inverse'});
});