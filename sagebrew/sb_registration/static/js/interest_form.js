$( document ).ready(function() {
    $('#id_select_all').click(function(event) {
        var $that = $(this);
        $(':checkbox').each(function() {
            this.checked = $that.is(':checked');
        });
    });

    $("#id_specific_interests").width("350px").select2({
        placeholder: "Select what you care about",
        allowClear: true
    });
});
