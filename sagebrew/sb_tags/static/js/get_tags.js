/*global $, jQuery, ajaxSecurity, Bloodhound*/
$(document).ready(function () {
    var engine = new Bloodhound({
        local: [
            {"value": "fiscal"},
            {"value": "pension"},
            {"value": "income"},
            {"value": "taxes"},
            {"value": "foreign_policy"},
            {"value": "russia"},
            {"value": "middle-east"},
            {"value": "iraq"},
            {"value": "social"},
            {"value": "lgbtqia"},
            {"value": "feminism"},
            {"value": "education"},
            {"value": "education-reform"},
            {"value": "university"},
            {"value": "financial-aid"},
            {"value": "science"},
            {"value": "mathematics"},
            {"value": "biology"},
            {"value": "chemistry"},
            {"value": "physics"},
            {"value": "fracking"},
            {"value": "environment"},
            {"value": "climate-change"},
            {"value": "natural-disaster"},
            {"value": "drugs"},
            {"value": "war-on-drugs"},
            {"value": "marijuana"},
            {"value": "substance-abuse"},
            {"value": "agriculture"},
            {"value": "organic"},
            {"value": "holistic"},
            {"value": "GMOs"},
            {"value": "defense"},
            {"value": "military"},
            {"value": "navy"},
            {"value": "military-budget"},
            {"value": "renewable-energy"},
            {"value": "nuclear-power"},
            {"value": "wind-power"},
            {"value": "energy"},
            {"value": "health"},
            {"value": "medical"},
            {"value": "cancer"},
            {"value": "obesity"},
            {"value": "space"},
            {"value": "space-exploration"},
            {"value": "space-shuttle"},
            {"value": "planet"}
        ],
        datumTokenizer: function (d) {
            return Bloodhound.tokenizers.whitespace(d.value);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });

    engine.initialize();
    $('#sb_tag_box').tokenfield({
        limit: 5,
        typeahead: [null, {source: engine.ttAdapter()}],
        delimiter: [",", " ", "'", ".", "*", "_"]
    });
    $.ajaxSetup({beforeSend: function (xhr, settings) {
        ajaxSecurity(xhr, settings);
    }});
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/tags/get_tags/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            var tags = data.tags;
            engine.add(tags);
        }
    });
});