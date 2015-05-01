/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    "use strict";
    $(window).unload(function () {
        var objectList = [];
        $(".js-page-object").each(function () {
            objectList.push($(this).data('object_uuid'));
        });
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajaxSecurity(xhr, settings);
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            async: false,
            url: "/docstore/update_neo_api/",
            data: JSON.stringify({
                'object_uuids': objectList
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            error: function (XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
        });
    });
});