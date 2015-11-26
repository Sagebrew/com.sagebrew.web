var usStates = [

];


function findAncestor (el, cls) {
    while ((el = el.parentElement) && !el.classList.contains(cls));
    return el;
}


function radioSelector(selectedElement) {
    "use strict";
    if(selectedElement.classList.contains("radio-selected")){
        selectedElement.classList.remove("radio-selected");
    } else {
        // this.closest('.block-container-radio').getElementsByClassName('radio-image-selector');
        // The above works but is not supported in IE
        // This makes sure you're only deselecting elements within the current
        // block container rather than on the whole page. Incase you have multiple
        // block selections
        var elements = findAncestor(selectedElement, 'block-container-radio').getElementsByClassName('radio-image-selector');
        for(var i = 0; i < elements.length; i++){
            elements[i].classList.remove("radio-selected");
        }
        selectedElement.classList.add("radio-selected");
    }
}

document.addEventListener("DOMContentLoaded", function() {
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
            } else if (this.id === "state-selection"){
                document.getElementById('state-input').classList.remove('hidden');
                document.getElementById('pac-input').classList.add('hidden');
            } else if (this.id === "federal-selection"){
                document.getElementById('state-input').classList.remove('hidden');
                document.getElementById('pac-input').classList.add('hidden');
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
    var nativedatalist = !!('list' in document.createElement('input')) &&
        !!(document.createElement('datalist') && window.HTMLDataListElement);

    if (!nativedatalist) {
        $('input[list]').each(function () {
            var availableTags = $('#' + $(this).attr("list")).find('option').map(function () {
                return this.value;
            }).get();
            $(this).autocomplete({ source: availableTags });
        });
    }
    init();
});

function initAutocomplete() {
    // TODO Mostly repeat code from locations.js in new architecture
    var latitude = 42.3314;
    var longitude = -83.0458;
    var affectedArea = null;
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
}

function init() {
    "use strict";
    // TODO Repeat code from locations.js in new architecture
    var s = document.createElement("script");
    s.type = "text/javascript";
    // s.src  = "https://maps.googleapis.com/maps/api/js?key=" + settings.google_maps + "&libraries=places&callback=setupAutoSearchMaps";
    s.src  = "https://maps.googleapis.com/maps/api/js?key=" + "AIzaSyDYSN_Flb7jJVswYVf-9pG4UMBPId3zlys" + "&libraries=places&callback=setupAutoSearchMaps";
    window.setupAutoSearchMaps = function(){
        initAutocomplete();
    };
    $("head").append(s);
}
