var Handlebars = require('handlebars'),
    request = require('api').request,
    createFlagTemplate = require('../templates/create_flag.hbs');


export function load() {
    Handlebars.registerPartial('create_flag', createFlagTemplate);
    var $app = $(".app-sb");
    $app
        .on('show.bs.modal', '#flagModal', function(event) {
            var button = $(event.relatedTarget),
                flagTarget = button.data('href'),
                objectUUID = button.data('parent_id'),
                modal = $(this);
            modal.data('flag_target', flagTarget);
            modal.data('object_uuid', objectUUID);
        })
        .on('click', '#flag_modal_submit', function () {
            var flagModal = $('#flagModal');
            $("#flag_modal_submit").attr("disabled", "disabled");
            request.post({
                url: flagModal.data('flag_target'),
                data: JSON.stringify({
                    content: $("textarea.flag_content_reason").val(),
                    flag_type: $('#flag_content').find('input:radio:checked').val()
                })
            }).done(function() {
                var flagObjectUUID = flagModal.data('object_uuid');
                $("#flag_" + flagObjectUUID).replaceWith('<button class="btn sb_btn_icon" type="button"><i class="fa fa-flag sb_btn_icon sb_btn_icon_purple sb_span_icon"></i></button>');
                $("#flag_modal_submit").removeAttr("disabled");
                $('textarea.flag_content_reason').val("");
                $('#wmd-preview-0').html("");
                flagModal.modal('hide');
            }).fail(function () {
                $("#flag_modal_submit").removeAttr("disabled");
                flagModal.modal('hide');
            });
        });
}