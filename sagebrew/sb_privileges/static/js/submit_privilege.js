$(document).ready(function(){
    $(".submit_privilege_form").click(function(event){
        event.preventDefault();
        var action_data = {};
        var action_form = $('#action_choice_form').serializeArray();
        $.each(action_form, function(){
            if(action_data[this.name] !== undefined) {
                if (!action_data[this.name].push) {
                    action_data[this.name] = [action_data[this.name]];
                }
                action_data[this.name].push(this.value || '');
            } else {
                action_data[this.name] = this.value || '';
            }
        });
        var req_data = {};
        var req_form = $('#requirement_choice_form').serializeArray();
        $.each(req_form, function(){
            if(req_data[this.name] !== undefined) {
                if (!req_data[this.name].push) {
                    req_data[this.name] = [req_data[this.name]];
                }
                req_data[this.name].push(this.value || '');
            } else {
                req_data[this.name] = this.value || '';
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/privilege/create/privilege/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "name": $("#id_privilege_name").val(),
                "actions": action_data['action[]'],
                "requirements": req_data['requirement[]']
            }),
            dataType: "json",
            success: function(data){
                alert(data);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});