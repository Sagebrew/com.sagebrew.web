$( document ).ready(function() {
	$(".submit_edit-action").click(function(event){
		event.preventDefault();
        if(typeof(Storage) !== "undefined") {
            placeID = localStorage.getItem('questionPlaceID');
            latitude = localStorage.getItem('questionLatitude');
            longitude = localStorage.getItem('questionLongitude');
            affected_area = localStorage.getItem('questionAffectedArea');
        } else {
            placeID = document.getElementById('location-id').innerHTML;
            latitude = document.getElementById('location-lat').innerHTML;
            longitude = document.getElementById('location-long').innerHTML;
            affected_area = document.getElementById('location-area').innerHTML;
        }
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/v1/questions/" + $('.submit_edit-action').data('object_uuid') + "/solution_count/",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var data_dict = {};
                if (data["solution_count"] == 0) {
                    data_dict = {
                        'content': $('textarea#wmd-input-0').val(),
                        'title': $('input#title_id').val(),
                        'external_location_id': placeID || null,
                        'latitude': latitude || null,
                        'longitude': longitude || null,
                        'affected_area': affected_area || null
                    };
                } else {
                    data_dict = {
                        'content': $('textarea#wmd-input-0').val(),
                        'external_location_id': placeID || null,
                        'latitude': latitude || null,
                        'longitude': longitude || null,
                        'affected_area': affected_area || null
                    };
                }

                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "PATCH",
                    url: "/v1/questions/" + $('.submit_edit-action').data('object_uuid') + "/",
                    data: JSON.stringify(data_dict),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        window.location.href = data['url'];
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        errorDisplay(XMLHttpRequest);
                    }
                });
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
    $(".cancel_edit_solution-action").click(function(event){
		window.location.href = "/conversations/";
	});
});