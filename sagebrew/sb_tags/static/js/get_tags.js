/*global $, ajaxSecurity, Bloodhound*/
$(document).ready(function () {
    var engine = new Bloodhound({
        local: [
            {"value": "fiscal"},
            {"value": "foreign_policy"},
            {"value": "social"},
            {"value": "education"},
            {"value": "science"},
            {"value": "environment"},
            {"value": "drugs"},
            {"value": "agriculture"},
            {"value": "defense"},
            {"value": "energy"},
            {"value": "health"},
            {"value": "space"}
        ],
        datumTokenizer: function (d) {
            return Bloodhound.tokenizers.whitespace(d.value);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace
    }), next = "/v1/tags/suggestion_engine?exclude_base=true&page_size=500";
    engine.initialize();
    function loadTags(url) {
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: url,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                var tags = data.results;
                next = data.next;
                engine.add(tags);
                loadTags(next);
            }
        });
    }
    $('#sb_tag_box').tokenfield({
        limit: 5,
        typeahead: [null, {source: engine.ttAdapter()}],
        delimiter: [",", " ", "'", ".", "*", "_"]
    });
    $("#sb_tag_box-tokenfield").attr("name", "tag_box");
    loadTags(next);
});