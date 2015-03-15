$(document).ready(function () {
    $('#submit_action_form').click(function(event){
        event.preventDefault();
        var data = {};
        var form = $('#action_form_id').serializeArray();
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
        console.log(data);
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/privilege/create/action/",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                $(".action_form").remove();
                $(".get_action_form").removeAttr('disabled');
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    });
});