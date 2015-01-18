$('#id_account_type').change(function(){
    ($(this).val()=='sub') ? $(".credit_card_info").show() : $(".credit_card_info").hide();
});

$("#id_office").change(function(){
    ($(this).val()=='f46fbcda-9da8-11e4-9233-080027242395') ? $("#office_input").show() : $("#office_input").hide();
});