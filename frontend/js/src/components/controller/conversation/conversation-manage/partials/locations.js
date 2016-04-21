/*global google*/
var request = require('api').request,
    helpers = require('common/helpers');

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
    var zoomLevel = helpers.determineZoom(affectedArea);

    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: latitude, lng: longitude},
        zoom: zoomLevel,
        draggable: false,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: true,
        scrollwheel: false
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
    helpers.loadMap(initAutocomplete, "places");
}
