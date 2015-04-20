$(document).ready(function () {
    $("textarea.flag_content_reason").pagedownBootstrap();
    $('#flagModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var flag_target = button.data('href');
        var object_uuid = button.data('object_uuid');
        var modal = $(this);
        modal.data('flag_target', flag_target);
        modal.data('object_uuid', object_uuid);
        modal.modal('handleUpdate');
    });
    $('#flag_modal_submit').on('click', function (event) {
        var flag_modal = $('#flagModal');
        $("#flag_modal_submit").attr("disabled", "disabled");
        $.ajaxSetup(
            {
                beforeSend: function (xhr, settings) {
                    ajax_security(xhr, settings)
                }
            });
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: flag_modal.data('flag_target'),
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({
                    'content': $("textarea.flag_content_reason").val(),
                    'flag_type': $('#flag_content input:radio:checked').val()
                }),
                dataType: "json",
                success: function(data){
                    var object_uuid = flag_modal.data('object_uuid');
                    $("#flag_" + object_uuid).replaceWith('<i class="fa fa-flag sb_btn_icon sb_btn_icon_purple sb_span_icon"></i>');
                    $("#flag_modal_submit").removeAttr("disabled");
                    $('textarea.flag_content_reason').val("");
                    $('#wmd-preview-0').html("");
                    flag_modal.modal('hide');
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $("#flag_modal_submit").removeAttr("disabled");
                    if(XMLHttpRequest.status === 500){
                        $("#server_error").show();
                    }
                }
            });
    });
});
