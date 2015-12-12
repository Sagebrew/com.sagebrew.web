/*global google, Intercom*/
var request = require('api').request,
    radioSelector = require('common/radioimage').radioSelector,
    helpers = require('common/helpers'),
    templates = require('template_build/templates'),
    settings = require('settings').settings,
    locationKey = 'advocateMissionLocationID',
    locationName = "advocateMissionLocationName",
    levelKey = 'advocateMissionLevel',
    filterKey = 'advocateMissionLocationFilter',
    districtKey = 'advocateDistrict';


export function load() {
    var $app = $(".app-sb"),
        placeInput = document.getElementById('pac-input'),
        stateInput = document.getElementById('state-input'),
        startBtn = document.getElementById('js-start-btn'),
        districtSelector = document.getElementById('js-district-selector');
    if(typeof(Storage) !== "undefined") {
        // Clear out all of the storage for the page, we're starting a new mission!
        localStorage.removeItem(locationKey);
        localStorage.removeItem(filterKey);
        localStorage.removeItem(districtKey);
        localStorage.removeItem(locationName);
        localStorage.removeItem(levelKey);
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
        .on('click', '.radio-image-selector', function(event) {
            event.preventDefault();

            if (this.classList.contains("radio-selected") && this.classList.contains("js-level")) {
                // TODO: REUSE
                // If we select a level that was already selected we need to disable the inputs
                // and clear the currently selected position and re-disable positions and districts
                stateInput.disabled = true;
                placeInput.disabled = true;
                districtSelector.innerHTML = templates.district_holder();
                localStorage.removeItem(districtKey);
            } else {
                // TODO: REUSE
                // If we select a level, enable the inputs
                stateInput.disabled = false;
                placeInput.disabled = false;

                // A new level was selected, clear the positions and districts
                localStorage.removeItem(districtKey);
                if(this.id === "local-selection"){
                    // The local level was selected
                    stateInput.classList.add('hidden');
                    placeInput.classList.remove('hidden');
                    localStorage.setItem(levelKey, "local");
                    placeInput.value = "";
                }
            }
            radioSelector(this);
        })
        .on('change', '#js-district-selector select', function() {
            // TODO REUSE
            // A district has been selected, we're at the bottom of the page
            // enable the start button and store off the final item needed for
            // federal and state campaigns
            localStorage.setItem(districtKey, this.options[this.selectedIndex].innerHTML);
            // Since after the selection a click event isn't raised we need to add this to ensure
            // the user can move forward without needing to click somewhere
            startBtn.disabled = false;
        })
        .on('click', '.registration', function() {
            // TODO REUSE
            // Some additional logic to ensure the startBtn only goes on when it should for both local and
            // Federal/State (district vs non-district)
            if(localStorage.getItem(filterKey) === "local"){
                // Local positions don't have districts so since a position has been selected enable the button
                startBtn.disabled = false;
            } else if(localStorage.getItem(filterKey) === "local" ){
                // We need to have a position selected before allowing the user to click the start button
                // so since none has been selected disable it.
                startBtn.disabled = true;
            }
        })
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

function districtSelection(level, stateInput, placeInput) {
    "use strict";
    /**
     * If the user had previous selected local we need to clear out
     * the running area since the location on the map now represents
     * what they had selected for local. This causes issues for grabbing
     * the position and districts as the place id is set to an incorrect location.
     */
    if(localStorage.getItem(filterKey) === "local"){
        localStorage.removeItem(locationKey);
        stateInput.selectedIndex = 0;
    }
    stateInput.classList.remove('hidden');
    placeInput.classList.add('hidden');
    localStorage.removeItem(districtKey);
    localStorage.setItem(filterKey, level);

    // We do this like this so we don't bind or try to change a element that is consistently
    // changing. It enables us to bind to the parent div that remains stable and eliminates
    // race conditions.
    document.getElementById('js-district-selector').innerHTML = templates.district_holder();
}


function fillDistricts(filterParam) {
    // TODO REUSE
    var identifier = localStorage.getItem(locationKey);
    var url = "/v1/locations/" + identifier + "/district_names/?lookup=external_id";
    if (filterParam !== "" && filterParam !== undefined){
        url = url + "&filter=" + filterParam;
    }
    console.log(url);
    request.get({url: url})
        .done(function (data) {
            console.log(data)
            var context, districtList = [], name;
            for(var i=0; i < data.results.length; i++) {
                name = data.results[i];
                context = {name: name};
                districtList.push(context);
            }
            document.getElementById('js-district-selector').innerHTML = templates.district_options({districts: districtList});
        });
}

function initAutocomplete() {
    // TODO REUSE
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
    autocomplete.setTypes(['(cities)']);
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

    function callback(results, status) {
        // TODO REUSE
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            var place = results[0];
            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(12);
            }
            localStorage.setItem(locationKey, place.place_id);
            request.post({url: '/v1/locations/async_add/', data: JSON.stringify(place)});
        }
        fillDistricts('federal');
    }
}

