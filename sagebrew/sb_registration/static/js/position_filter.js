/*global $, jQuery, ajaxSecurity, Bloodhound, errorDisplay*/
$(document).ready(function () {
    var engine = new Bloodhound({
        local: [
            {"value": "Alabama"},
            {"value": "Alaska"},
            {"value": "Arizona"},
            {"value": "Arkansas"},
            {"value": "California"},
            {"value": "Colorado"},
            {"value": "Connecticut"},
            {"value": "Delaware"},
            {"value": "Florida"},
            {"value": "Georgia"},
            {"value": "Hawaii"},
            {"value": "Idaho"},
            {"value": "Illinois"},
            {"value": "Indiana"},
            {"value": "Iowa"},
            {"value": "Kansas"},
            {"value": "Kentucky"},
            {"value": "Louisiana"},
            {"value": "Maine"},
            {"value": "Maryland"},
            {"value": "Massachusetts"},
            {"value": "Michigan"},
            {"value": "Minnesota"},
            {"value": "Mississippi"},
            {"value": "Missouri"},
            {"value": "Montana"},
            {"value": "Nebraska"},
            {"value": "Nevada"},
            {"value": "New Hampshire"},
            {"value": "New Jersey"},
            {"value": "New Mexico"},
            {"value": "New York"},
            {"value": "North Carolina"},
            {"value": "North Dakota"},
            {"value": "Ohio"},
            {"value": "Oklahoma"},
            {"value": "Oregon"},
            {"value": "Pennsylvania"},
            {"value": "Rhode Island"},
            {"value": "South Carolina"},
            {"value": "South Dakota"},
            {"value": "Tennessee"},
            {"value": "Texas"},
            {"value": "Utah"},
            {"value": "Vermont"},
            {"value": "Virginia"},
            {"value": "Washington"},
            {"value": "West Virginia"},
            {"value": "Wisconsin"},
            {"value": "Wyoming"}
        ],
        datumTokenizer: function (d) {
            return Bloodhound.tokenizers.whitespace(d.value);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });
    engine.initialize();
    $('#state')
        .on('tokenfield:createtoken', function (e) {
            var tokenArray;
            try {
                tokenArray = $('#state').tokenfield('getTokensList').split(', ');
            } catch (err) {
                tokenArray = $('#state').tokenfield('getTokensList');
            }
            if ($.inArray(e.attrs.value, tokenArray) > -1) {
                $(".tt-input").val("");
                return false;
            }
            for (var p in engine.local) {
                if (engine.local[p].value === e.attrs.value) {
                    return true;
                }
            }
            $.notify(
                {message: "Unrecognized state name! Please enter a valid state name or use our provided state names."},
                {type: "danger"});
            $(".tt-input").val("");
            return false;
        })
        .on('tokenfield:createdtoken', function (e) {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/locations/" + e.attrs.value + "/positions/render/",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    $("#position_wrapper").append(data);
                    $(".sb_btn").off().on("click", function (event) { // http://stackoverflow.com/questions/14969960/jquery-click-events-firing-multiple-times reason for off
                        event.preventDefault();
                        $(this).prop("disabled", true);
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "POST",
                            url: "/v1/campaigns/",
                            contentType: "application/json; charset=utf-8",
                            data: JSON.stringify({
                                "position": $(this).data("object_uuid")
                            }),
                            dataType: "json",
                            success: function (data) {
                                window.location.href = data.url;
                                console.log(data);
                            },
                            error: function (XMLHttpRequest, textStatus, errorThrown) {
                                console.log(XMLHttpRequest);
                                console.log(textStatus);
                                console.log(errorThrown);
                                errorDisplay(XMLHttpRequest);
                                $(this).prop('disabled', false);
                            }
                        });
                    });
                }
            });
        })
        .on('tokenfield:removedtoken', function (e) {
            var removeTokenStr = e.attrs.value.replace(/ /g, '');
            $("." + removeTokenStr).remove();
        })
        .tokenfield({
            limit: 50,
            typeahead: [null, {source: engine.ttAdapter()}],
            delimiter: [",", "'", ".", "*", "_"]
        });
    $("#js-president_selector").on("click", function (event) {
        console.log($(this).data("object_uuid"));
        event.preventDefault();
        $(this).prop("disabled", true);
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "position": $(this).data("object_uuid")
            }),
            dataType: "json",
            success: function (data) {
                window.location.href = data.url;
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
                $(this).prop('disabled', false);
            }
        });
    });
});