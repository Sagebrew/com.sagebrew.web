$( document ).ready(function() {

    $('.toggle-all').click(function() {
        console.log("here")
        $('#select_all_checkboxes input').each(function(inde, item) {
            var label = $("label[for='"+$(item).attr('id')+"']");
            $(label).toggleClass("checkbox  checkbox checked");
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

