/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    "use strict";
    $("textarea.flag_content_reason").pagedownBootstrap();
    $('#flagModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget),
            flagTarget = button.data('href'),
            objectUUID = button.data('object_uuid'),
            modal = $(this);
        modal.data('flag_target', flagTarget);
        modal.data('object_uuid', objectUUID);
    });
    $('#flag_modal_submit').on('click', function (event) {
        var flagModal = $('#flagModal');
        $("#flag_modal_submit").attr("disabled", "disabled");
        $.ajaxSetup(
            {
                beforeSend: function (xhr, settings) {
                    ajaxSecurity(xhr, settings);
                }
            }
        );
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: flagModal.data('flag_target'),
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                'content': $("textarea.flag_content_reason").val(),
                'flag_type': $('#flag_content input:radio:checked').val()
            }),
            dataType: "json",
            success: function (data) {
                var flagObjectUUID = flagModal.data('object_uuid');
                $("#flag_" + flagObjectUUID).replaceWith('<i class="fa fa-flag sb_btn_icon sb_btn_icon_purple sb_span_icon"></i>');
                $("#flag_modal_submit").removeAttr("disabled");
                $('textarea.flag_content_reason').val("");
                $('#wmd-preview-0').html("");
                flagModal.modal('hide');
            },
            error: function (XMLHttpRequest) {
                $("#flag_modal_submit").removeAttr("disabled");
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
        });
    });
});
