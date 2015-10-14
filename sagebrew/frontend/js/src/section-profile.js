/**
 * @file
 * -- Contains all functionality for the profile section.
 */
var sagebrew = require('sagebrew'),
    representatives = require('./components/section/profile/representatives');


representatives.loadReps();

/**
 * Friendship Controller.
 */
$(".sb_wall").on('click', '[data-ctrl=friendship]', function(event) {
    console.log(event);
    var $target  = $(event.target);
    console.log($target.data("user"));
   console.log("fuck");

});

var $element = $('[data-ctrl=friendship]');
console.log($element.length);
$element.on('click', function(event) {
   console.log("test");
});