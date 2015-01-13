$('#id_account_type').change(function(){
    ($(this).val()=='sub') ? $(".credit_card_info").show() : $(".credit_card_info").hide();
});