$(document).ready(function(){
    $(".submit_privilege_form").click(function(event){
        var action_forms = [];
        var requirement_forms = [];
        $(".action_form").each(function(i, obj){
            var form_dict = {};
            var serialized = obj.serializeArray();
            console.log(serialized);
            $.each(serialized, function(){
                if (form_dict[this.name] !== undefined) {
                    if(!form_dict[this.name].push){
                        form_dict[this.name] = [form_dict[this.name]];
                    }
                    form_dict[this.name].push(this.value || '');
                } else {
                    form_dict[this.name] = this.value || '';
                }
            });
            action_forms.push(form_dict);
        });
        $(".requirement_form").each(function(i, obj){
            var form_data = new FormData(obj);
            requirement_forms.push(form_data.serializeArray());
            console.log(requirement_forms);
        });
       var privilege_form = new FormData(".privilege_form");
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/privilege/create/privilege/",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "privilege": privilege_form,
                "actions": action_forms,
                "requirements": requirement_forms
            }),
            dataType: "json",
            success: function(data){
            }
        });
    });
});