/**
 * @file
 * Helper functions that aren't global.
 */

var settings = require('./../settings').settings;

/**
 * Get cookie based by name.
 * @param name
 * @returns {*}
 */
export function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i += 1) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Check if HTTP method requires CSRF.
 * @param method
 * @returns {boolean}
 */
export function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


/**
 * Parse URL args.
 * if no arg key is passed, return all the args.
 */
export function args(arg) {
    var select;

    if(typeof arg === 'undefined'){
        select = false;
    } else {
        select = arg;
    }

    var elements = window.location.pathname.split("/");

    for (var item in elements) {
        if (elements.hasOwnProperty(item)) {
            if (!elements[item]) {
                elements.splice(item, 1);
            }
        }
    }

    if (select && elements[select]) {
        return elements[select];
    }
    else {
        return elements;
    }

}

/**
 * Generate a uuid
 */
export function generateUuid() {
  function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
  }

  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
        s4() + '-' + s4() + s4() + s4();
}

/**
 * Find the first parent element containing a given class of the provided element.
 * Something like:
 * this.closest('.block-container-radio').getElementsByClassName('radio-image-selector');
 * would result in an equivalent output but is not supported by IE
 * @param el - child element
 * @param cls - class we're looking parents for
 * @returns {*}
 */
export function findAncestor (el, cls) {
    while ((el = el.parentElement) && !el.classList.contains(cls));
    return el;
}


export function loadMap(callbackFxn, libraries = "places") {
    "use strict";
    var s = document.createElement("script");
    s.type = "text/javascript";
    s.src  = "https://maps.googleapis.com/maps/api/js?key=" + settings.google_maps + "&libraries=" + libraries + "&callback=setupAutoSearchMaps";
    window.setupAutoSearchMaps = function(){
        callbackFxn();
    };
    $("head").append(s);
}

export function determineZoom(affectedArea){
    "use strict";
    var zoomLevel = 12;
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

    return zoomLevel;
}
