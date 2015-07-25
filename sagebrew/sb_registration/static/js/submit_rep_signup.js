$(document).ready(function(){
    $("#regForm").submit(function(event){
        var $form = $(this);
        $form.find('button').prop('disabled', true);
        if ($("#id_account_type").val() === "sub"){
            Stripe.card.createToken($form, stripeResponseHandler);
        }
        Stripe.bankAccount.createToken({
            country: 'US',
            routingNumber: $('.routing_number').val(),
            accountNumber: $('.account_number').val()
        }, stripeBankHandler);
        return false;
    });
});

function stripeBankHandler(status, response) {
    var $form = $('#regForm');
    if (response.error) {
        $form.find('.payment-errors').text(response.error.message);
        $form.find('button').prop('disabled', false);
    } else {
        var token = response.id;
        $form.append($('<input type="hidden" name="stripeBankToken"/>').val(token));
        $form.get(0).submit();
    }
}

function stripeResponseHandler(status, response) {
    var $form = $('#regForm');
    if (response.error) {
        $form.find('.payment-errors').text(response.error.message);
        $form.find('button').prop('disabled', false);
    } else {
        var token = response.id;
        $form.append($('<input type="hidden" name="stripeCardToken"/>').val(token));
    }
}

