$(document).ready(function() {
    $.ajaxSetup({beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/tags/get_tags/",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            console.log(data);
            var tags = data['tags'];
            console.log(tags);
           var engine = new Bloodhound({
  local: tags,
  datumTokenizer: function(d) {
    return Bloodhound.tokenizers.whitespace(d.value);
  },
  queryTokenizer: Bloodhound.tokenizers.whitespace
});

engine.initialize();
            $('#sb_tag_box').tokenfield({
                typeahead: [null, {source: engine.ttAdapter()}],
                delimiter: [",", " ","'",".","*", "_"]
            });
        }
    })
});