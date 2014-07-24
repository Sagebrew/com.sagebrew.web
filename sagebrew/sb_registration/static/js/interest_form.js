$( document ).ready(function() {

    $('.toggle-all').click(function() {
        var toggle_class = $('.toggle-all').attr('class');
        var lastClass = toggle_class.substr( toggle_class.lastIndexOf(' ') + 1);
        $('#select_all_checkboxes input').each(function(inde, item) {
            var label = $("label[for='"+$(item).attr('id')+"']")[1];
            var label_class = $(label).attr('class');
            var label_last = label_class.substr( label_class.lastIndexOf(' ') + 1);
            if(lastClass !== "checked") {
                if (label_last !== 'checked') {
                    $(label).addClass('checked')
                }
            } else {
                if (label_last === 'checked'){
                    $(label).removeClass('checked')
                }
            }
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

