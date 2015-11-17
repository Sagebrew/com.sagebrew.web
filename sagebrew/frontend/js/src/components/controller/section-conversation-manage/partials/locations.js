/*global google*/
var request = require('./../../../api').request,
    settings = require('./../../../settings').settings;

function initAutocomplete() {
    if(typeof(Storage) !== "undefined") {
        localStorage.removeItem('questionPlaceID');
        localStorage.removeItem('questionLatitude');
        localStorage.removeItem('questionLongitude');
        localStorage.removeItem('questionAffectedArea');
    }
    var latitude = parseFloat(document.getElementById('location-lat').innerHTML) || 42.3314;
    var longitude = parseFloat(document.getElementById('location-long').innerHTML) || -83.0458;
    var affectedArea = document.getElementById('location-area').innerHTML || null;
    var zoomLevel = 12;
    // TODO: Duplicated code, need to move this into a fxn, export it, and call it
    if(affectedArea !== null) {
        if((affectedArea.match(/,/g) || []).length === 0){
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
    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: latitude, lng: longitude},
        zoom: zoomLevel,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: true
    });
    var input = document.getElementById('pac-input');

    var autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.setTypes(['(regions)']);
    autocomplete.bindTo('bounds', map);
    var marker = new google.maps.Marker({
        map: map,
        anchorPoint: new google.maps.Point(42.3314, -83.0458)
    });
    autocomplete.addListener('place_changed', function() {
        marker.setVisible(false);

        var place = autocomplete.getPlace();
        if (!place.geometry) {
            window.alert("Autocomplete's returned place contains no geometry");
            return;
        }

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(12);
        }
        marker.setIcon(({
            url: place.icon,
            size: new google.maps.Size(71, 71),
            origin: new google.maps.Point(0, 0),
            anchor: new google.maps.Point(17, 34),
            scaledSize: new google.maps.Size(35, 35)
        }));
        marker.setPosition(place.geometry.location);
        marker.setVisible(true);
        var placeID = place.place_id,
            affectedArea = place.formatted_address;
        latitude = place.geometry.location.lat();
        longitude = place.geometry.location.lng();
        if(typeof(Storage) !== "undefined") {
            localStorage.setItem('questionPlaceID', placeID);
            localStorage.setItem('questionLatitude', latitude);
            localStorage.setItem('questionLongitude', longitude);
            localStorage.setItem('questionAffectedArea', affectedArea);
        } else {
            document.getElementById('location-id').innerHTML = placeID;
            document.getElementById('location-lat').innerHTML = latitude;
            document.getElementById('location-long').innerHTML = longitude;
            document.getElementById('location-area').innerHTML = affectedArea;
        }

        request.post({url: '/v1/locations/cache/', data: JSON.stringify(place)});
    });
}

export function init() {
    "use strict";
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.src  = "https://maps.googleapis.com/maps/api/js?key=" + settings.google_maps + "&libraries=places&callback=setupAutoSearchMaps";
    window.setupAutoSearchMaps = function(){
        initAutocomplete();
    };
    $("head").append(s);
}
