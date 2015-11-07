/*global google*/
var request = require('./../../../api').request;

// Required to provide global function to be called with callback
function displayMap() {
    var timeOutId = 0,
        questionID = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0];
    request.get({url: '/v1/questions/' + questionID + '/?expedite=true'})
        .done(function (data) {
            var zoomLevel = 1;
            if(data.longitude !== undefined && data.longitude !== null) {
                zoomLevel = 5;
            }
            var latLong = {lat: data.latitude || 37.09024, lng: data.longitude || -95.71289100000001};
            var map = new google.maps.Map(document.getElementById('map'), {
                zoom: zoomLevel,
                center: latLong,
                disableDefaultUI: true
            });
            if(data.longitude !== undefined && data.longitude !== null) {
                new google.maps.Marker({
                    position: latLong,
                    map: map,
                    title: data.affected_area
                });
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
