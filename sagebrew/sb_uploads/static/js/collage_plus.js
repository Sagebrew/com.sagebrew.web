$(document).ready(function(){
    $(".sb_collage").each(function(i, obj){
        $(obj).collagePlus({
            'targetHeight': 200,
            'fadeSpeed': 'slow',
            'effect': 'effect-1',
            'direction': 'horizontal',
            'allowPartialLastRow': false
        });
    })
});