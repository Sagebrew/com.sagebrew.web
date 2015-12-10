/*global google*/
var request = require('api').request;

// Required to provide global function to be called with callback
function displayMap() {
    var timeOutId = 0,
        questionID = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0];
    request.get({url: '/v1/questions/' + questionID + '/?expedite=true'})
        .done(function (data) {
            // TODO: Duplicated code, need to move this into a fxn, export it, and call it
            var zoomLevel = 1;
            if(data.longitude !== undefined && data.longitude !== null) {
                if((data.affected_area.match(/,/g) || []).length === 0){
                    zoomLevel = 3;
                } else if ((data.affected_area.match(/,/g) || []).length === 1) {
                    zoomLevel = 5;
                } else if ((data.affected_area.match(/,/g) || []).length === 2) {
                    zoomLevel = 12;
                } else if ((data.affected_area.match(/,/g) || []).length === 3) {
                    zoomLevel = 14;
                } else if ((data.affected_area.match(/,/g) || []).length >= 4) {
                    zoomLevel = 14;
                }
            }
            var latLong = {lat: data.latitude || 37.09024, lng: data.longitude || -95.71289100000001};
            var map = new google.maps.Map(document.getElementById('map'), {
                zoom: zoomLevel,
                center: latLong,
                disableDefaultUI: true
            });
            if(data.longitude !== undefined && data.longitude !== null) {
                if((data.affected_area.match(/,/g) || []).length > 1){
                    new google.maps.Marker({
                        position: latLong,
                        map: map,
                        title: data.affected_area
                    });
                }
            }
        })
        .fail(function(){
            timeOutId = setTimeout(displayMap, 1000);
        });

}

export function init() {
    "use strict";
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.src  = "https://maps.googleapis.com/maps/api/js?key=AIzaSyDYSN_Flb7jJVswYVf-9pG4UMBPId3zlys&callback=initMap";
    window.initMap = function(){
        displayMap();
    };
    $("head").append(s);
}
