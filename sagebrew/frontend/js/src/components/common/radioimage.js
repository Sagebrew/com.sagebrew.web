/**
 * @file
 * This is the logic necessary to add our radio image selector logic. See
 * public_office_mission.html template for example usage.
 */

var helpers = require('./helpers');

export function radioSelector(selectedElement) {
    "use strict";
    if(selectedElement.classList.contains("radio-selected")){
        selectedElement.classList.remove("radio-selected");
    } else {
        // this.closest('.block-container-radio').getElementsByClassName('radio-image-selector');
        // The above works but is not supported in IE
        // This makes sure you're only deselecting elements within the current
        // block container rather than on the whole page. Incase you have multiple
        // block selections
        var elements = helpers.findAncestor(selectedElement, 'block-container-radio').getElementsByClassName('radio-image-selector');
        for(var i = 0; i < elements.length; i++){
            elements[i].classList.remove("radio-selected");
        }
        selectedElement.classList.add("radio-selected");
    }
}