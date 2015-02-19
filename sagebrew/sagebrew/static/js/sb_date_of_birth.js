$(document).ready(function () {
    $('input[name="birthday"]').bind('keyup',function(){
        var strokes = $(this).val().length;
        if(strokes === 2 || strokes === 5){
            var thisVal = $(this).val();
            thisVal += '/';
            $(this).val(thisVal);
        }
    });
});