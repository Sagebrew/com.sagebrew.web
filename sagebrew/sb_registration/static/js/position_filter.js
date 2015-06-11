/*global $, jQuery, ajaxSecurity, Bloodhound*/
$(document).ready(function () {
    var engine = new Bloodhound({
        local: [
            {"value": "Alabama"},
            {"value": "Alaska"},
            {"value": "Arizona"},
            {"value": "Arkansas"},
            {"value": "California"},
            {"value": "Colorado"},
            {"value": "Connecticut"},
            {"value": "Delaware"},
            {"value": "Florida"},
            {"value": "Georgia"},
            {"value": "Hawaii"},
            {"value": "Idaho"},
            {"value": "Illinois"},
            {"value": "Indiana"},
            {"value": "Iowa"},
            {"value": "Kansas"},
            {"value": "Kentucky"},
            {"value": "Louisiana"},
            {"value": "Maine"},
            {"value": "Maryland"},
            {"value": "Massachusetts"},
            {"value": "Michigan"},
            {"value": "Minnesota"},
            {"value": "Mississippi"},
            {"value": "Missouri"},
            {"value": "Montana"},
            {"value": "Nebraska"},
            {"value": "Nevada"},
            {"value": "New Hampshire"},
            {"value": "New Jersey"},
            {"value": "New Mexico"},
            {"value": "New York"},
            {"value": "North Carolina"},
            {"value": "North Dakota"},
            {"value": "Ohio"},
            {"value": "Oklahoma"},
            {"value": "Oregon"},
            {"value": "Pennsylvania"},
            {"value": "Rhode Island"},
            {"value": "South Carolina"},
            {"value": "South Dakota"},
            {"value": "Tennessee"},
            {"value": "Texas"},
            {"value": "Utah"},
            {"value": "Vermont"},
            {"value": "Virginia"},
            {"value": "Washington"},
            {"value": "West Virginia"},
            {"value": "Wisconsin"},
            {"value": "Wyoming"}
        ],
        datumTokenizer: function (d) {
            return Bloodhound.tokenizers.whitespace(d.value);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });
    engine.initialize();
    $('#state')
        .on('tokenfield:createtoken', function (e) {
            for (var p in engine.local) {
                if (engine.local[p].value === e.attrs.value) {
                    return true;
                }
            }
            $.notify(
                {message: "Unrecognized state name! Please enter a valid state name or use our provided state names."},
                {type: "danger"});
            return false;
        })
        .tokenfield({
            limit: 50,
            typeahead: [null, {source: engine.ttAdapter()}],
            delimiter: [",", " ", "'", ".", "*", "_"]
        });
});