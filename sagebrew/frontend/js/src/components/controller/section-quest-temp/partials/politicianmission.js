/*global google*/
var request = require('./../../../api').request,
    radioSelector = require('./../../../common/radioimage').radioSelector,
    helpers = require('./../../../common/helpers'),
    templates = require('./../../../template_build/templates');


export function load() {
    var $app = $(".app-sb");
    $app
        .on('click', '.radio-image-selector', function(event) {
            event.preventDefault();
            if(this.classList.contains("radio-selected")){
                document.getElementById('state-input').disabled = true;
                document.getElementById('pac-input').disabled = true;
            } else {
                document.getElementById('state-input').disabled = false;
                document.getElementById('pac-input').disabled = false;
            }
            radioSelector(this);
            if(this.id === "local-selection"){
                document.getElementById('state-input').classList.add('hidden');
                document.getElementById('pac-input').classList.remove('hidden');
                document.getElementById('district-row').classList.add('hidden');
            } else if (this.id === "state-selection"){
                document.getElementById('state-input').classList.remove('hidden');
                document.getElementById('pac-input').classList.add('hidden');
                document.getElementById('district-row').classList.remove('hidden');
            } else if (this.id === "federal-selection"){
                document.getElementById('state-input').classList.remove('hidden');
                document.getElementById('pac-input').classList.add('hidden');
                document.getElementById('district-row').classList.remove('hidden');
            }
        })
        //
        // TODO repeat code as what we use in section-profile friends.js
        .on('mouseenter', ".js-hover-overlay-activate", function(event) {
            event.preventDefault();
            var $this = $(this),
            overlay = $this.parent().parent().find(".sb-overlay");
            overlay.height($this.height());
            overlay.fadeIn('fast');
        })

        //
        // Remove overlay when mouse leaves card region
        .on('mouseleave', '.sb-overlay', function(event) {
            event.preventDefault();
            $(this).fadeOut('fast');
            $(".sb-profile-not-friend-element-image").removeClass("active");
        });
    var context = {name: "President", image_path: "https://sagebrew.local.dev/static/images/city.png"};
    var template = templates.position_image_radio;
    document.getElementById('js-position-selector').innerHTML = template(context);
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
            if (query === "New York") {
                query = query + " State, United States";
            } else {
                query = query + ", United States";
            }
            var request = {
                query: query
            };
            var service = new google.maps.places.PlacesService(map);
            service.textSearch(request, callback);
        });

    var autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.setTypes(['(regions)']);
    autocomplete.bindTo('bounds', map);
    autocomplete.addListener('place_changed', function() {
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



        request.post({url: '/v1/locations/cache/', data: JSON.stringify(place)});
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
        }
    }
}

