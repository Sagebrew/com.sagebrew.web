/*global $, ajaxSecurity, Bloodhound*/
$(document).ready(function () {
    var engine = new Bloodhound({
        prefetch: "/v1/tags/suggestion_engine_v2/",
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });
    engine.initialize();
    $('#sb_tag_box').tokenfield({
        limit: 5,
        typeahead: [null, {source: engine.ttAdapter()}],
        delimiter: [",", " ", "'", ".", "*", "_"]
    });
    $("#sb_tag_box-tokenfield").attr("name", "tag_box");
    $(".token-input.tt-hint").addClass('tag_input')
});