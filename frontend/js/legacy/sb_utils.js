/*global $, jQuery, guid, enableSinglePostFunctionality, errorDisplay, lightbox, Autolinker*/



function getOrCreateExpandedURLs(regExp, content, editButton) {
    var regexMatches = content.match(regExp),
        promises = [];
    if (regexMatches) {
        $.unique(regexMatches);
        $.each(regexMatches, function (key, value) {
            $(editButton).attr("disabled", "disabled");
            $(editButton).spin('small');
            var request = $.ajax({
                xhrFields: {withCredentials: true},
                type: "POST",
                url: "/v1/urlcontent/",
                data: JSON.stringify({
                    'object_uuid': guid(),
                    'url': value
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    $(editButton).removeAttr('disabled');
                    $(editButton).spin(false);
                },
                error: function (XMLHttpRequest) {
                    $(editButton).removeAttr('disabled');
                    $(editButton).spin(false);
                }
            });
            promises.push(request);
        });
        return promises;
    }
    return promises;
}


function cloneForm(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '_TOTAL_FORMS').val();
    newElement.find(':input').each(function () {
        var name = $(this).attr('name').replace('-' + (total - 1) + '-', '-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function () {
        var newFor = $(this).attr('for').replace('-' + (total - 1) + '-', '-' + total + '-');
        $(this).attr('for', newFor);
    });
    total += 1;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}

function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i += 1) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] === sParam) {
            return sParameterName[1];
        }
    }
}

function foggyClosed(populatedIds) {
    $.each(populatedIds, function(index, value) {
        var toBeFogged = $(".sb_blurred_content#sb_content_" + value);
        toBeFogged.foggy({
            blurRadius: 15,
            opacity: 0.95
        });
        toBeFogged.click(function (event) {
            event.preventDefault();
            $(this).foggy(false);
        });
    });
}
