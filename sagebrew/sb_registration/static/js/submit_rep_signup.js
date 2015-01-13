$(document).ready(function(){
    $("#regForm").submit(function(event){
        var $form = $(this);
        $form.find('button').prop('disabled', true);
        Stripe.card.createToken($form, stripeResponseHandler);
        return false;
    })
});

function stripeResponseHandler(status, response) {
    var $form = $('#regForm');
    if (response.error) {
        $form.find('.payment-errors').text(response.error.message);
        $form.find('button').prop('disabled', false);
    } else {
        var token = response.id;
        $form.append($('<input type="hidden" name="stripeToken"/>').val(token));
    }
}

