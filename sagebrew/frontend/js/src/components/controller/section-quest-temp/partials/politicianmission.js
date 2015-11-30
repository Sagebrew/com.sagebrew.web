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
            } else if (this.id === "Senator") {
                console.log('here')
            } else if (this.id === "House Representative") {
                console.log('here')
            }
        });

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
        fillPositions(place.place_id);
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
            fillPositions(place.place_id);
            fillDistricts(place.place_id);
            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(12);
            }
        }
    }
}

function fillDistricts(identifier, filter="") {
    "use strict";
    var url = "/v1/locations/" + identifier + "/district_names/?lookup=external_id";
    request.get({url: url})
        .done(function (data) {
            var context, districtList = [], name;
            for(var i=0; i < data.results.length; i++) {
                name = data.results[i];
                context = {name: name};
                districtList.push(context);
            }
            document.getElementById('js-district-selector').innerHTML = templates.district_options({districts: districtList});
        });
}

function fillPositions (identifier, filter="") {
    "use strict";
    var url = "/v1/locations/" + identifier + "/position_names/?lookup=external_id";
    console.log(url);
    request.get({url:url})
        .done(function(data) {
            var context, positionList = [], name,
                image_path;
            for(var i=0; i < data.results.length; i++) {
                name = data.results[i];
                // TODO simplify with types rather than each position
                if(name === "Senator"){
                    image_path = "https://sagebrew.local.dev/static/images/council.png"
                } else if (name === "House Representative"){
                    image_path = "https://sagebrew.local.dev/static/images/council.png"
                } else if (name === "President") {
                    image_path = "https://sagebrew.local.dev/static/images/executive.png"
                } else if (name === "Governor") {
                    image_path = "https://sagebrew.local.dev/static/images/executive.png"
                } else if (name === "City Council") {
                    image_path = "https://sagebrew.local.dev/static/images/council.png"
                } else if (name === "Mayor") {
                    image_path = "https://sagebrew.local.dev/static/images/executive.png"
                }
                context = {
                    name: name,
                    image_path: image_path
                };
                positionList.push(context);
            }
            document.getElementById('js-position-selector').innerHTML = templates.position_image_radio({positions: positionList});
        });


}

