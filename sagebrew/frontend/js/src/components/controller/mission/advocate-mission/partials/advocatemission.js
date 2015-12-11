/*global google, Intercom*/
var request = require('api').request,
    radioSelector = require('common/radioimage').radioSelector,
    helpers = require('common/helpers'),
    templates = require('template_build/templates'),
    settings = require('settings').settings,
    locationKey = 'politicianMissionLocationID',
    locationName = "politicianMissionLocationName",
    positionKey = 'politicianMissionPosition';


export function load() {
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
    helpers.loadMap(initAutocomplete, "places");
}



function initAutocomplete() {
    var $app = $(".app-sb");
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

    $app
        .on('change', '#state-input', function() {
            "use strict";
            var query = this.options[this.selectedIndex].innerHTML;
            localStorage.setItem(locationName, query);
            if (query === "New York") {
                query = query + " State, United States";
            } else {
                query = query + ", United States";
            }
            var requestQuery = {
                query: query
            };
            var service = new google.maps.places.PlacesService(map);
            service.textSearch(requestQuery, callback);
        });

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
        localStorage.removeItem(positionKey);
        request.post({url: '/v1/locations/async_add/', data: JSON.stringify(place)});
    });

    function callback(results, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            var place = results[0];
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
            localStorage.removeItem(positionKey);
            request.post({url: '/v1/locations/async_add/', data: JSON.stringify(place)});
        }
    }
}

