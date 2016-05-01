 /*global Intercom, google, Bloodhound*/
var request = require('api').request,
    radioSelector = require('common/radioimage').radioSelector,
    helpers = require('common/helpers'),
    positionHolderTemplate = require('../templates/position_holder.hbs'),
    districtHolderTemplate = require('../templates/district_holder.hbs'),
    districtOptionsTemplate = require('../templates/district_options.hbs'),
    positionImageTemplate = require('../templates/position_image_radio.hbs'),
    settings = require('settings').settings,
    filterKey = 'politicianMissionLocationFilter',
    locationKey = 'politicianMissionLocationID',
    locationName = "politicianMissionLocationName",
    positionKey = 'politicianMissionPosition',
    districtKey = 'politicianMissionDistrict',
    levelKey = 'politicianMissionLevel',
    stateUpper = "state_upper",
    stateLower = "state_lower";


export function load() {
    var $app = $(".app-sb"),
        stateInput = document.getElementById('state-input'),
        placeInput = document.getElementById('pac-input'),
        districtRow = document.getElementById('district-row'),
        startBtn = document.getElementById('js-start-btn'),
        districtSelector = document.getElementById('js-district-selector'),
        positionSelector = document.getElementById('js-position-selector'),
        positionInputRow = document.getElementById('position-input-row'),
        greyPage = document.getElementById('sb-greyout-page'),
        positionInput = $('#position-input'),
        positionInputCharCount = $("#js-position-char-count"),
        positionInputCharLimit = 240;
    // We just loaded the app, jam in some place holders to look nice.
    // Didn't include directly in the Django template so we don't have duplicate formatting
    positionSelector.innerHTML = positionHolderTemplate({static_url: settings.static_url});
    if(typeof(Storage) !== "undefined") {
        // Clear out all of the storage for the page, we're starting a new mission!
        localStorage.removeItem(locationKey);
        localStorage.removeItem(filterKey);
        localStorage.removeItem(positionKey);
        localStorage.removeItem(districtKey);
        localStorage.removeItem(locationName);
        localStorage.removeItem(levelKey);
    }
    var engine = new Bloodhound({
        local: ["District Attorney", "Mayor", "Governor", "City Council",
            "Lieutenant Governor", "Treasurer", "Controller", "Auditor",
            "Attorney General", "Superintendent of Schools",
            "Agriculture Commissioner", "Natural Resources Commissioner",
            "Labor Commissioner", "Public Service Commissioner",
            "Member of the State Board of Education", "Sheriff",
            "Chief of Police", "District Court of Appeals Judge",
            "Port Authority", "Member of Board of County Commissioners",
            "Circuit Judge", "Member of School Board", "Prosecuting Attorney",
            "Railroad Commissioner"],
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });
    engine.initialize();
    positionInput.typeahead(
        {
            highlight: true,
            hint: true
        },
        {
             source: engine
        });
    $("#position-input-tokenfield").attr("name", "tag_box");
    positionInput.bind('typeahead:select', function(ev, suggestion) {
        // Activate button after a suggestion has been selected
        startBtn.disabled = false;
        // Should remove the previous item to ensure that only the most
        // recent input is passed to the endpoint
        localStorage.removeItem(positionKey);
        localStorage.setItem(positionKey, suggestion);
    });
    positionInput.keyup(function() {
        var $this = $(this),
            positionInputWrapper = $(".position-input-wrapper");
        helpers.characterCountRemaining(positionInputCharLimit, positionInput, positionInputCharCount);
        if ($this.val().length <= 0) {
            startBtn.disabled = true;

        } else if ($this.val().length > positionInputCharLimit) {
            startBtn.disabled = true;
            positionInputWrapper.removeClass("has-success");
            positionInputWrapper.addClass("has-error");
        } else {
            positionInputWrapper.removeClass("has-error");
            positionInputWrapper.addClass("has-success");
            // Should remove the previous item to ensure that only the most
            // recent input is passed to the endpoint
            localStorage.removeItem(positionKey);
            localStorage.setItem(positionKey, $this.val());
            // Activate button after a position has been input
            startBtn.disabled = false;
        }
    });
    $app
        .on('click', '.radio-image-selector', function(event) {
            event.preventDefault();
            if(this.id !== "Other") {
                positionInputRow.classList.add('hidden');
            }
            if(this.classList.contains("radio-selected") && this.classList.contains("js-level")){
                // If we select a level that was already selected we need to disable the inputs
                // and clear the currently selected position and re-disable positions and districts
                stateInput.disabled = true;
                placeInput.disabled = true;
                positionSelector.innerHTML = positionHolderTemplate({static_url: settings.static_url});
                districtSelector.innerHTML = districtHolderTemplate();
                localStorage.removeItem(positionKey);
                localStorage.removeItem(districtKey);
                localStorage.removeItem(locationKey);
                localStorage.removeItem(locationName);
                localStorage.removeItem(levelKey);
                stateInput.selectedIndex = 0;
                startBtn.disabled = true;
            } else if(this.classList.contains("radio-selected") && this.classList.contains("js-position")) {
                // If we select a position that was already selected we need to remove the districts and
                // the stored off position. We also need to disable the start button until a district is selected
                localStorage.removeItem(districtKey);
                localStorage.removeItem(positionKey);
                positionInputRow.classList.add('hidden');
                districtSelector.innerHTML = districtHolderTemplate();
            } else {
                // If we select a level, enable the inputs
                stateInput.disabled = false;
                placeInput.disabled = false;

                // A new level was selected, clear the positions and districts
                localStorage.removeItem(positionKey);
                localStorage.removeItem(districtKey);
                if(this.id === "local-selection"){
                    // The local level was selected
                    stateInput.classList.add('hidden');
                    placeInput.classList.remove('hidden');
                    districtRow.classList.add('hidden');
                    localStorage.setItem(filterKey, "local");
                    localStorage.setItem(levelKey, "local");
                    positionSelector.innerHTML = positionHolderTemplate({static_url: settings.static_url});
                    placeInput.value = "";
                } else if (this.id === "state-selection"){
                    // The state level was selected
                    // Don't set level key here because we need to determine if we're
                    // in state upper or state lower
                    districtSelection('state', stateInput, placeInput, positionSelector);

                } else if (this.id === "federal-selection"){
                    // The federal level was selected
                    // Hide the district row since president and senator don't need it and
                    // we want to ensure we cover hiding it if state was already selected.
                    districtRow.classList.add('hidden');
                    localStorage.setItem(levelKey, "federal");
                    districtSelection('federal', stateInput, placeInput, positionSelector);
                } else{
                    // We've selected a position
                    // Since a position has been selected we can get the districts and enable the selector,
                    // if we need to.
                    localStorage.removeItem(districtKey);
                    checkIfDistricts(this.id, districtRow, positionInputRow);
                }
            }
            radioSelector(this);
        })
        .on('change', '#js-district-selector select', function() {
            // A district has been selected, we're at the bottom of the page
            // enable the start button and store off the final item needed for
            // federal and state campaigns
            localStorage.setItem(districtKey, this.options[this.selectedIndex].innerHTML);
            // Since after the selection a click event isn't raised we need to add this to ensure
            // the user can move forward without needing to click somewhere
            startBtn.disabled = false;
        })
        .on('click', '.registration', function() {
            // Some additional logic to ensure the startBtn only goes on when it should for both local and
            // Federal/State (district vs non-district)
            if(localStorage.getItem(filterKey) === "local" && localStorage.getItem(positionKey) !== null){
                // Local positions don't have districts so since a position has been selected enable the button
                startBtn.disabled = false;
            } else if(localStorage.getItem(filterKey) === "local" && localStorage.getItem(positionKey) === null){
                // We need to have a position selected before allowing the user to click the start button
                // so since none has been selected disable it.
                startBtn.disabled = true;
            }

            // Enabling the button is handled by on change of js-district-selector select above
            if(localStorage.getItem(filterKey) === "state" && localStorage.getItem(districtKey) === null) {
                startBtn.disabled = true;
                if(localStorage.getItem(positionKey) !== null) {
                    startBtn.disabled = false;
                }
            }
            if(localStorage.getItem(filterKey) === "federal") {
                if(localStorage.getItem(positionKey) === "Senator" || localStorage.getItem(positionKey) === "President") {
                    // Presidents and Senators don't have districts so we can enable the start button
                    startBtn.disabled = false;
                } else if (localStorage.getItem(districtKey) === null){
                    // If we're not talking about Presidents or Senators we need a district so disable the
                    // start button until a district is selected.
                    startBtn.disabled = true;
                    if(localStorage.getItem(positionKey) !== null) {
                        startBtn.disabled = false;
                    }
                }
            }
        })
        .on('click', '#js-start-btn', function(){
            greyPage.classList.remove('sb_hidden');
            Intercom('trackEvent', 'setup-mission');
            Intercom('trackEvent', 'setup-political-mission');
            var location;
            if(localStorage.getItem(filterKey) !== "local"){
                location = localStorage.getItem(locationName);
            } else {
                location = localStorage.getItem(locationKey);
            }
            request.post({
                url: "/v1/missions/",
                data: JSON.stringify({
                    focus_name: localStorage.getItem(positionKey),
                    district: localStorage.getItem(districtKey),
                    level: localStorage.getItem(levelKey),
                    location_name: location,
                    focus_on_type: "position"
                })
            }).done(function (data) {
                greyPage.classList.add('sb_hidden');
                if(settings.profile.quest.account_verified !== "unverified") {
                    // TODO this needs to be swapped out with actual location of one pager
                    window.location.href = "/missions/" + data.id + "/" + data.slug + "/manage/epic/edit/";
                } else {
                    window.location.href = "/missions/account/";
                }
            });
        })
        .on('click', '#js-cancel-btn', function(event){
            event.preventDefault();
            window.location.href = "/quests/" + settings.user.username;
        });
    helpers.loadMap(initAutocomplete, "places");
}

function districtSelection(level, stateInput, placeInput, positionSelector) {
    /**
     * If the user had previous selected local we need to clear out
     * the running area since the location on the map now represents
     * what they had selected for local. This causes issues for grabbing
     * the position and districts as the place id is set to an incorrect location.
     */
    if(localStorage.getItem(filterKey) === "local"){
        // If the level was previously local and now we're changin it we need
        // to remove the location key and reset the state input to 0.
        localStorage.removeItem(locationKey);
        stateInput.selectedIndex = 0;
        positionSelector.innerHTML = positionHolderTemplate({static_url: settings.static_url});
    }
    stateInput.classList.remove('hidden');
    placeInput.classList.add('hidden');
    localStorage.removeItem(districtKey);
    localStorage.setItem(filterKey, level);
    if(localStorage.getItem(locationKey) !== null){
        /**
         * If we have a location already selected let's fill up the positions.
         * If the user goes and selects something else the positions will update
         * based on the callback but this will save them a step if they end up
         * changing from state to federal since they are the same list of states.
         */
        fillPositions(localStorage.getItem(locationKey));
    }

    /**
     * If a level is selected the district should always be set to disabled and the position
     * removed from local storage.
     * On the first selection we have not yet selected a location or a position
     * and districts should only be filled out after both of those have been
     * selected.
     *
     * On a second click we are deselecting a level so we should disable them (this is handled above).
     *
     * If the level is selected after a position has been selected then the positions
     * will be removed and we need to repopulate the districts after a new position has
     * been selected. But people should not be able to select the district in that time period
     */
    localStorage.removeItem(positionKey);
    // We do this like this so we don't bind or try to change a element that is consistently
    // changing. It enables us to bind to the parent div that remains stable and eliminates
    // race conditions.
    document.getElementById('js-district-selector').innerHTML = districtHolderTemplate();
}

function checkIfDistricts(identifier, districtRow, positionInputRow) {
    if(identifier.indexOf('Senator') > -1) {
        localStorage.setItem(positionKey, identifier);
        if (localStorage.getItem(filterKey) === "state"){
            districtRow.classList.remove('hidden');
            localStorage.setItem(levelKey, stateUpper);
            fillDistricts(stateUpper);
        } else {
            localStorage.setItem(levelKey, "federal");
            districtRow.classList.add('hidden');
        }
    } else if(identifier.indexOf("House Representative") > -1) {
        localStorage.setItem(positionKey, identifier);
        districtRow.classList.remove('hidden');
        if (localStorage.getItem(filterKey) === "state"){
            localStorage.setItem(levelKey, stateLower);
            fillDistricts(stateLower);
        } else {
            localStorage.setItem(levelKey, "federal");
            fillDistricts("federal");
        }
    } else if(identifier === "Other") {
        localStorage.setItem(levelKey, localStorage.getItem(filterKey));
        positionInputRow.classList.remove('hidden');
        districtRow.classList.add('hidden');
    } else {
        localStorage.setItem(positionKey, identifier);
        districtRow.classList.add('hidden');
    }
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
        draggable: false,
        scrollwheel: false
    });
    var input = document.getElementById('pac-input');

    $app
        .on('change', '#state-input', function() {
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
        fillPositions(place.place_id);
        localStorage.setItem(locationKey, place.place_id);

        /**
         * If a location is selected the district should always be replaced by the holder and the position
         * removed from local storage
         * This selection always changes the positions and districts which is why this is necessary
         */
        localStorage.removeItem(positionKey);
        document.getElementById('js-district-selector').innerHTML = districtHolderTemplate();
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
            fillPositions(place.place_id);
            localStorage.setItem(locationKey, place.place_id);
            /**
             * If a location is selected the district should always be replaced by the holder and the position
             * removed from local storage
             * This selection always changes the positions and districts which is why this is necessary
             */
            localStorage.removeItem(positionKey);
            document.getElementById('js-district-selector').innerHTML = districtHolderTemplate();
            request.post({url: '/v1/locations/async_add/', data: JSON.stringify(place)});
        }
    }
}

function fillDistricts(filterParam) {
    var identifier = localStorage.getItem(locationKey);
    var url = "/v1/locations/" + identifier + "/district_names/?lookup=external_id";
    if (filterParam !== "" && filterParam !== undefined){
        url = url + "&filter=" + filterParam;
    }
    request.get({url: url})
        .done(function (data) {
            var context, districtList = [], name;
            for(var i=0; i < data.results.length; i++) {
                name = data.results[i];
                context = {name: name};
                districtList.push(context);
            }
            document.getElementById('js-district-selector').innerHTML = districtOptionsTemplate({districts: districtList, option_holder: "Select a District"});
        });
}

function fillPositions(identifier) {
    var url = "/v1/locations/" + identifier + "/position_names/?lookup=external_id",
        locality=localStorage.getItem(filterKey);
    // We're filling the position list with a new set of positions so remove the old one
    localStorage.removeItem(positionKey);
    if (locality !== "" && locality !== undefined){
        url = url + "&filter=" + locality;
    }
    request.get({url:url})
        .done(function(data) {
            var context, positionList = [], name,
                image_path;
            for(var i=0; i < data.results.length; i++) {
                name = data.results[i];
                if(name.indexOf("Senator") > -1){
                    image_path = settings.static_url + "images/legislative_bw.png";
                } else if (name.indexOf("House Representative") > -1){
                    image_path = settings.static_url + "images/legislative_bw.png";
                } else if (name === "President") {
                    image_path = settings.static_url + "images/executive_bw.png";
                } else if (name === "Governor") {
                    image_path = settings.static_url + "images/executive_bw.png";
                } else if (name === "City Council") {
                    image_path = settings.static_url + "images/legislative_bw.png";
                } else if (name === "Mayor") {
                    image_path = settings.static_url + "images/executive_bw.png";
                } else {
                    image_path = settings.static_url + "images/legislative_bw.png";
                }
                context = {
                    name: name,
                    image_path: image_path
                };
                positionList.push(context);
            }
            context = {
                name: "Other",
                image_path: settings.static_url + "images/glass_bw.png"
            };
            positionList.push(context);
            document.getElementById('js-position-selector').innerHTML = positionImageTemplate({positions: positionList});
        });


}

