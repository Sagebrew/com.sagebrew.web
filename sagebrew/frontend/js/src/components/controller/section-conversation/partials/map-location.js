/*global google*/


// Required to provide global function to be called with callback
function displayMap() {
    var latLong = {lat: 42.524756, lng: -83.536327};
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: latLong,
        disableDefaultUI: true
    });
    new google.maps.Marker({
        position: latLong,
        map: map,
        title: 'Wixom'
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
