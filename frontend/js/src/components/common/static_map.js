/*global google*/
var request = require('api').request;

// Required to provide global function to be called with callback
function displayMap(url, mapID, externalID) {
    var timeOutId = 0;
    request.get({url: url})
        .done(function (data) {
            var zoomLevel = 1,
                latLong = {lat: data.latitude || 37.09024, lng: data.longitude || -95.71289100000001},
                map = new google.maps.Map(document.getElementById(mapID), {
                    zoom: zoomLevel,
                    center: latLong,
                    disableDefaultUI: true,
                    draggable: false,
                    scrollwheel: false
                }),
                affectedArea = data.affected_area || data.formatted_location_name;
            if (latLong.lng !== undefined && latLong.lng !== null) {
                if ((affectedArea.match(/,/g) || []).length === 0) {
                    zoomLevel = 3;
                } else if ((affectedArea.match(/,/g) || []).length === 1) {
                    zoomLevel = 5;
                } else if ((affectedArea.match(/,/g) || []).length === 2) {
                    zoomLevel = 12;
                } else if ((affectedArea.match(/,/g) || []).length === 3) {
                    zoomLevel = 14;
                } else if ((affectedArea.match(/,/g) || []).length >= 4) {
                    zoomLevel = 14;
                }
            }
            if (externalID) {
                var placeID = data.location.external_id,
                    geocoder = new google.maps.Geocoder();
                if (placeID === null) {
                    geocoder.geocode({'address': data.formatted_location_name}, function (results, status) {
                        if (status === google.maps.GeocoderStatus.OK) {
                            if (results[0]) {
                                map.setZoom(zoomLevel);
                                map.setCenter(results[0].geometry.location);
                                var marker = new google.maps.Marker({
                                    map: map,
                                    position: results[0].geometry.location
                                });
                                marker.setVisible(false);
                            }
                        }
                    });
                } else {
                    geocoder.geocode({'placeId': placeID}, function (results, status) {
                        if (status === google.maps.GeocoderStatus.OK) {
                            if (results[0]) {
                                map.setZoom(zoomLevel);
                                map.setCenter(results[0].geometry.location);
                                var marker = new google.maps.Marker({
                                    map: map,
                                    position: results[0].geometry.location
                                });
                                marker.setVisible(false);
                            }
                        }
                    });
                }

            } else {
                if (data.longitude !== undefined && data.longitude !== null) {
                    if ((data.affected_area.match(/,/g) || []).length > 1) {
                        var marker = new google.maps.Marker({
                            position: latLong,
                            map: map,
                            title: data.affected_area
                        });
                        marker.setVisible(false);
                        map.setZoom(zoomLevel);
                    }
                }
            }
        })
        .fail(function(){
            timeOutId = setTimeout(displayMap, 1000);
        });

}

export function init(url, mapID, externalID) {
    "use strict";
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.src  = "https://maps.googleapis.com/maps/api/js?key=AIzaSyDYSN_Flb7jJVswYVf-9pG4UMBPId3zlys&callback=initMap";
    window.initMap = function(){
        displayMap(url, mapID, externalID);
    };
    $("head").append(s);
}
