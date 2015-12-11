/*global google, Intercom*/
var request = require('api').request,
    helpers = require('common/helpers'),
    templates = require('template_build/templates'),
    settings = require('settings').settings,
    locationKey = 'advocateMissionLocationID',
    districtKey = 'advocateDistrict';


export function load() {
    var $app = $(".app-sb");
    if(typeof(Storage) !== "undefined") {
        // Clear out all of the storage for the page, we're starting a new mission!
        localStorage.removeItem(locationKey);
        localStorage.removeItem(districtKey);
    }
    var engine = new Bloodhound({
        prefetch: "/v1/tags/suggestion_engine_v2/",
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });
    engine.initialize();
    $('#advocate-input').typeahead(
        {
            highlight: true,
            hint: true
        },
        {
             source: engine
        });
    $("#advocate-input-tokenfield").attr("name", "tag_box");

    $app
        .on('click', '#js-start-btn', function(){
            request.post({
                url: "/v1/missions/",
                data: JSON.stringify({
                    focus_name: $('#advocate-input').val(),
                    district: localStorage.getItem(districtKey),
                    location_name: localStorage.getItem(locationKey),
                    focus_on_type: "advocacy"
                })
            }).done(function () {
                window.location.href = "/quests/" + settings.user.username + "/";
            });
        })
        .on('click', '#js-cancel-btn', function(event){
            event.preventDefault();
            window.location.href = "/quests/" + settings.user.username;
        });
    helpers.loadMap(initAutocomplete, "places");
}



function initAutocomplete() {
    var latitude = 42.3314;
    var longitude = -83.0458;
    var affectedArea = null;
    var zoomLevel = helpers.determineZoom(affectedArea);
    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: latitude, lng: longitude},
        zoom: zoomLevel,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: true,
        scrollwheel: false
    });
    var input = document.getElementById('pac-input');

    var autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.setTypes(['(regions)']);
    autocomplete.bindTo('bounds', map);


    autocomplete.addListener('place_changed', function() {
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            window.alert("Sorry we couldn't find that location. Please try another or contact us.");
            return;
        }

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(12);
        }
        localStorage.setItem(locationKey, place.place_id);

        /**
         * If a location is selected the district should always be replaced by the holder and the position
         * removed from local storage
         * This selection always changes the positions and districts which is why this is necessary
         */
        request.post({url: '/v1/locations/async_add/', data: JSON.stringify(place)});
    });
}

