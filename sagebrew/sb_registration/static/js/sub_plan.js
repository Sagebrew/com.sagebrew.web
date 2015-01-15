$('#id_account_type').change(function(){
    ($(this).val()=='sub') ? $(".credit_card_info").show() : $(".credit_card_info").hide();
});

$("#id_office").change(function(){
    ($(this).val()=='other') ? $("#office_input").show() : $("#office_input").hide();
});