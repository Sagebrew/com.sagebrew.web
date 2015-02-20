$(document).ready(function () {
    $('#birthday').keyup(function (e) {
            if (e.keyCode != 193 && e.keyCode != 111) {
                console.log(e.keyCode);
                if (e.keyCode != 8) {
                    if ($(this).val().length == 2) {
                        $(this).val($(this).val() + "/");
                    } else if ($(this).val().length == 5) {
                        $(this).val($(this).val() + "/");
                    }
                } else {
                    var temp = $(this).val();
                    if ($(this).val().length == 5) {
                        $(this).val(temp.substring(0, 4));
                    } else if ($(this).val().length == 2) {
                        $(this).val(temp.substring(0, 1));
                    }
                }
            } else {
                var temp = $(this).val();
                var tam = $(this).val().length;
                $(this).val(temp.substring(0, tam-1));
            }
    });
});