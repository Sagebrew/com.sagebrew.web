(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/**
 * @file
 * Load reps onto page.
*/
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.loadReps = loadReps;
var request = require('sagebrew').request;

/**
 * Get the username of whoever owns the profile.
 * TODO: Come up with a better way to do this.
 */
function getUsername() {
    return $("#user_info").data("page_user_username");
}

/**
 * TODO:turn reps into some sort of tree structure so that we can get all the
 * info from one request.
 */

function loadReps() {
    $(document).ready(function () {
        var username = getUsername();
        var rcp = request.get({ url: '/v1/profiles/' + username + '/president/?html=true' }),
            rcs = request.get({ url: '/v1/profiles/' + username + '/senators/?html=true' }),
            rchr = request.get({ url: '/v1/profiles/' + username + '/house_representative/?html=true' }),
            rps = request.get({ url: '/v1/profiles/' + username + '/possible_senators/?html=true' }),
            rphr = request.get({ url: '/v1/profiles/' + username + '/possible_house_representatives/?html=true' }),
            rpp = request.get({ url: '/v1/profiles/' + username + '/possible_presidents/?html=true' }),
            rplr = request.get({ url: '/v1/profiles/' + username + '/possible_local_representatives/?html=true' });

        $.when(rcp, rcs, rchr, rps, rphr, rpp, rplr).done(function (dcp, dcs, dchr, dps, dphr, dpp, dplr) {
            $("#president_wrapper").append(dcp[0]);
            $("#senator_wrapper").append(dcs[0]);
            $("#house_rep_wrapper").append(dchr[0]);
            $("#potential_senator_wrapper").append(dps[0]);
            $("#potential_rep_wrapper").append(dphr[0]);
            $("#potential_president_wrapper").append(dpp[0]);
            $("#potential_local_wrapper").append(dplr[0]);
        });
    });
}

},{"sagebrew":"sagebrew"}],2:[function(require,module,exports){
/**
 * @file
 * -- Contains all functionality for sections.
 */
'use strict';

var sagebrew = require('sagebrew'),
    representatives = require('./components/section/profile/representatives');

representatives.loadReps();

},{"./components/section/profile/representatives":1,"sagebrew":"sagebrew"}]},{},[2])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9jb21wb25lbnRzL3NlY3Rpb24vcHJvZmlsZS9yZXByZXNlbnRhdGl2ZXMuanMiLCIvVXNlcnMvbXdpc25lci9Qcm9qZWN0cy9zYWdlYnJldy9jb20uc2FnZWJyZXcud2ViL3NhZ2VicmV3L2Zyb250ZW5kL2pzL3NyYy9zZWN0aW9uLXByb2ZpbGUuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7Ozs7Ozs7O0FDSUEsSUFBSSxPQUFPLEdBQUcsT0FBTyxDQUFDLFVBQVUsQ0FBQyxDQUFDLE9BQU8sQ0FBQzs7Ozs7O0FBTTFDLFNBQVMsV0FBVyxHQUFHO0FBQ25CLFdBQU8sQ0FBQyxDQUFDLFlBQVksQ0FBQyxDQUFDLElBQUksQ0FBQyxvQkFBb0IsQ0FBQyxDQUFDO0NBQ3JEOzs7Ozs7O0FBTU0sU0FBUyxRQUFRLEdBQUc7QUFDdkIsS0FBQyxDQUFDLFFBQVEsQ0FBQyxDQUFDLEtBQUssQ0FBQyxZQUFZO0FBQzFCLFlBQUksUUFBUSxHQUFHLFdBQVcsRUFBRSxDQUFDO0FBQzdCLFlBQUksR0FBRyxHQUFHLE9BQU8sQ0FBQyxHQUFHLENBQUMsRUFBQyxHQUFHLEVBQUUsZUFBZSxHQUFHLFFBQVEsR0FBRyx1QkFBdUIsRUFBQyxDQUFDO1lBQzlFLEdBQUcsR0FBRyxPQUFPLENBQUMsR0FBRyxDQUFDLEVBQUMsR0FBRyxFQUFFLGVBQWUsR0FBRyxRQUFRLEdBQUcsc0JBQXNCLEVBQUMsQ0FBQztZQUM3RSxJQUFJLEdBQUcsT0FBTyxDQUFDLEdBQUcsQ0FBQyxFQUFDLEdBQUcsRUFBRSxlQUFlLEdBQUcsUUFBUSxHQUFHLGtDQUFrQyxFQUFDLENBQUM7WUFDMUYsR0FBRyxHQUFHLE9BQU8sQ0FBQyxHQUFHLENBQUMsRUFBQyxHQUFHLEVBQUUsZUFBZSxHQUFHLFFBQVEsR0FBRywrQkFBK0IsRUFBQyxDQUFDO1lBQ3RGLElBQUksR0FBRyxPQUFPLENBQUMsR0FBRyxDQUFDLEVBQUMsR0FBRyxFQUFFLGVBQWUsR0FBRyxRQUFRLEdBQUcsNENBQTRDLEVBQUMsQ0FBQztZQUNwRyxHQUFHLEdBQUcsT0FBTyxDQUFDLEdBQUcsQ0FBQyxFQUFDLEdBQUcsRUFBRSxlQUFlLEdBQUcsUUFBUSxHQUFHLGlDQUFpQyxFQUFDLENBQUM7WUFDeEYsSUFBSSxHQUFHLE9BQU8sQ0FBQyxHQUFHLENBQUMsRUFBQyxHQUFHLEVBQUUsZUFBZSxHQUFHLFFBQVEsR0FBRyw0Q0FBNEMsRUFBQyxDQUFDLENBQUM7O0FBRXpHLFNBQUMsQ0FBQyxJQUFJLENBQUMsR0FBRyxFQUFFLEdBQUcsRUFBRSxJQUFJLEVBQUUsR0FBRyxFQUFFLElBQUksRUFBRSxHQUFHLEVBQUUsSUFBSSxDQUFDLENBQUMsSUFBSSxDQUFDLFVBQVUsR0FBRyxFQUFFLEdBQUcsRUFBRSxJQUFJLEVBQUUsR0FBRyxFQUFFLElBQUksRUFBRSxHQUFHLEVBQUUsSUFBSSxFQUFFO0FBQzlGLGFBQUMsQ0FBQyxvQkFBb0IsQ0FBQyxDQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQztBQUN2QyxhQUFDLENBQUMsa0JBQWtCLENBQUMsQ0FBQyxNQUFNLENBQUMsR0FBRyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7QUFDckMsYUFBQyxDQUFDLG9CQUFvQixDQUFDLENBQUMsTUFBTSxDQUFDLElBQUksQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO0FBQ3hDLGFBQUMsQ0FBQyw0QkFBNEIsQ0FBQyxDQUFDLE1BQU0sQ0FBQyxHQUFHLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQztBQUMvQyxhQUFDLENBQUMsd0JBQXdCLENBQUMsQ0FBQyxNQUFNLENBQUMsSUFBSSxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7QUFDNUMsYUFBQyxDQUFDLDhCQUE4QixDQUFDLENBQUMsTUFBTSxDQUFDLEdBQUcsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO0FBQ2pELGFBQUMsQ0FBQywwQkFBMEIsQ0FBQyxDQUFDLE1BQU0sQ0FBQyxJQUFJLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQztTQUNqRCxDQUFDLENBQUM7S0FDTixDQUFDLENBQUM7Q0FDTjs7Ozs7Ozs7O0FDbkNELElBQUksUUFBUSxHQUFHLE9BQU8sQ0FBQyxVQUFVLENBQUM7SUFDOUIsZUFBZSxHQUFHLE9BQU8sQ0FBQyw4Q0FBOEMsQ0FBQyxDQUFDOztBQUc5RSxlQUFlLENBQUMsUUFBUSxFQUFFLENBQUMiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiLyoqXG4gKiBAZmlsZVxuICogTG9hZCByZXBzIG9udG8gcGFnZS5cbiovXG52YXIgcmVxdWVzdCA9IHJlcXVpcmUoJ3NhZ2VicmV3JykucmVxdWVzdDtcblxuLyoqXG4gKiBHZXQgdGhlIHVzZXJuYW1lIG9mIHdob2V2ZXIgb3ducyB0aGUgcHJvZmlsZS5cbiAqIFRPRE86IENvbWUgdXAgd2l0aCBhIGJldHRlciB3YXkgdG8gZG8gdGhpcy5cbiAqL1xuZnVuY3Rpb24gZ2V0VXNlcm5hbWUoKSB7XG4gICAgcmV0dXJuICQoXCIjdXNlcl9pbmZvXCIpLmRhdGEoXCJwYWdlX3VzZXJfdXNlcm5hbWVcIik7XG59XG5cbi8qKlxuICogVE9ETzp0dXJuIHJlcHMgaW50byBzb21lIHNvcnQgb2YgdHJlZSBzdHJ1Y3R1cmUgc28gdGhhdCB3ZSBjYW4gZ2V0IGFsbCB0aGVcbiAqIGluZm8gZnJvbSBvbmUgcmVxdWVzdC5cbiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGxvYWRSZXBzKCkge1xuICAgICQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uICgpIHtcbiAgICAgICAgdmFyIHVzZXJuYW1lID0gZ2V0VXNlcm5hbWUoKTtcbiAgICAgICAgdmFyIHJjcCA9IHJlcXVlc3QuZ2V0KHt1cmw6ICcvdjEvcHJvZmlsZXMvJyArIHVzZXJuYW1lICsgJy9wcmVzaWRlbnQvP2h0bWw9dHJ1ZSd9KSxcbiAgICAgICAgICAgIHJjcyA9IHJlcXVlc3QuZ2V0KHt1cmw6ICcvdjEvcHJvZmlsZXMvJyArIHVzZXJuYW1lICsgJy9zZW5hdG9ycy8/aHRtbD10cnVlJ30pLFxuICAgICAgICAgICAgcmNociA9IHJlcXVlc3QuZ2V0KHt1cmw6ICcvdjEvcHJvZmlsZXMvJyArIHVzZXJuYW1lICsgJy9ob3VzZV9yZXByZXNlbnRhdGl2ZS8/aHRtbD10cnVlJ30pLFxuICAgICAgICAgICAgcnBzID0gcmVxdWVzdC5nZXQoe3VybDogJy92MS9wcm9maWxlcy8nICsgdXNlcm5hbWUgKyAnL3Bvc3NpYmxlX3NlbmF0b3JzLz9odG1sPXRydWUnfSksXG4gICAgICAgICAgICBycGhyID0gcmVxdWVzdC5nZXQoe3VybDogJy92MS9wcm9maWxlcy8nICsgdXNlcm5hbWUgKyAnL3Bvc3NpYmxlX2hvdXNlX3JlcHJlc2VudGF0aXZlcy8/aHRtbD10cnVlJ30pLFxuICAgICAgICAgICAgcnBwID0gcmVxdWVzdC5nZXQoe3VybDogJy92MS9wcm9maWxlcy8nICsgdXNlcm5hbWUgKyAnL3Bvc3NpYmxlX3ByZXNpZGVudHMvP2h0bWw9dHJ1ZSd9KSxcbiAgICAgICAgICAgIHJwbHIgPSByZXF1ZXN0LmdldCh7dXJsOiAnL3YxL3Byb2ZpbGVzLycgKyB1c2VybmFtZSArICcvcG9zc2libGVfbG9jYWxfcmVwcmVzZW50YXRpdmVzLz9odG1sPXRydWUnfSk7XG5cbiAgICAgICAgJC53aGVuKHJjcCwgcmNzLCByY2hyLCBycHMsIHJwaHIsIHJwcCwgcnBscikuZG9uZShmdW5jdGlvbiAoZGNwLCBkY3MsIGRjaHIsIGRwcywgZHBociwgZHBwLCBkcGxyKSB7XG4gICAgICAgICAgICAkKFwiI3ByZXNpZGVudF93cmFwcGVyXCIpLmFwcGVuZChkY3BbMF0pO1xuICAgICAgICAgICAgJChcIiNzZW5hdG9yX3dyYXBwZXJcIikuYXBwZW5kKGRjc1swXSk7XG4gICAgICAgICAgICAkKFwiI2hvdXNlX3JlcF93cmFwcGVyXCIpLmFwcGVuZChkY2hyWzBdKTtcbiAgICAgICAgICAgICQoXCIjcG90ZW50aWFsX3NlbmF0b3Jfd3JhcHBlclwiKS5hcHBlbmQoZHBzWzBdKTtcbiAgICAgICAgICAgICQoXCIjcG90ZW50aWFsX3JlcF93cmFwcGVyXCIpLmFwcGVuZChkcGhyWzBdKTtcbiAgICAgICAgICAgICQoXCIjcG90ZW50aWFsX3ByZXNpZGVudF93cmFwcGVyXCIpLmFwcGVuZChkcHBbMF0pO1xuICAgICAgICAgICAgJChcIiNwb3RlbnRpYWxfbG9jYWxfd3JhcHBlclwiKS5hcHBlbmQoZHBsclswXSk7XG4gICAgICAgIH0pO1xuICAgIH0pO1xufSIsIi8qKlxuICogQGZpbGVcbiAqIC0tIENvbnRhaW5zIGFsbCBmdW5jdGlvbmFsaXR5IGZvciBzZWN0aW9ucy5cbiAqL1xudmFyIHNhZ2VicmV3ID0gcmVxdWlyZSgnc2FnZWJyZXcnKSxcbiAgICByZXByZXNlbnRhdGl2ZXMgPSByZXF1aXJlKCcuL2NvbXBvbmVudHMvc2VjdGlvbi9wcm9maWxlL3JlcHJlc2VudGF0aXZlcycpO1xuXG5cbnJlcHJlc2VudGF0aXZlcy5sb2FkUmVwcygpO1xuXG5cblxuIl19
