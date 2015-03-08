$(document).ready(function () {
    $('#submit_requirement_form').click(function(event){
        event.preventDefault();
        var data = {};
        var form = $('#requirement_form_id').serializeArray();
        $.each(form, function(){
            if(data[this.name] !== undefined) {
                if (!data[this.name].push) {
                    data[this.name] = [data[this.name]];
                }
                data[this.name].push(this.value || '');
            } else {
                data[this.name] = this.value || '';
            }
        });
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/privilege/create/requirement/",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                $(".requirement_form").remove();
                $(".get_requirement_form").removeAttr('disabled');
            }
        });
    });
});