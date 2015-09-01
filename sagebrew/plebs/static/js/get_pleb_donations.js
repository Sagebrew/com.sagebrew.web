/*global $, jQuery, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    function cancelPledge() {
        $(".js-cancel-donation").off().on('click', function (){
            var objectID = $(this).data('object_uuid');
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "DELETE",
                url: "/v1/donations/" + objectID + "/",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    $('.js-donation-block-' + objectID).remove();
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    errorDisplay(XMLHttpRequest);
                }
            });
        });
    }
    cancelPledge();
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/v1/me/donations/?html=true",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#donation_wrapper").append(data.results);
            cancelPledge();
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            errorDisplay(XMLHttpRequest);
        }
    });
});