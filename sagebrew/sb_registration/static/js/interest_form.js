$( document ).ready(function() {
    $('#id_select_all').click(function(event) {
        var $that = $(this);
        $(':checkbox').each(function() {
            this.checked = $that.is(':checked');
        });
    });
    $("[data-toggle='tooltip']").tooltip('hide');

    $("#id_specific_interests").select2({
        placeholder: "Select what you care about",
        allowClear: true,
        width: "100%"
    });
    $(".tooltip").addClass(function() {
        if ($(this).prev().attr("data-tooltip-style")) {
        return "tooltip-" + $(this).prev().attr("data-tooltip-style");
      }
    });
});

