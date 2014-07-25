$( document ).ready(function() {
    /**
     * This is the function that selects all the fields and deselects all the
     * fields. It works even if fields are already selected or unselected.
     * It also assigns the value to the checkbox of true or false with the
     * end dot notation of .val(!ch).
     */
    $('.toggle-all').on('click', function() {
      var ch = $(this).find(':checkbox').prop('checked');
      $('#select_all_checkboxes').find('.checkbox-toggle :checkbox').checkbox(!ch ? 'check' : 'uncheck').val(!ch);
    });

    /**
     * Does individual checkboxes and when they are clicked assigns the value
     * associated with the checkbox input to either true or false since
     * it appears bootstrap/flat ui rely on the class of the label to change
     * between checked and a blank string rather then the actual value of the
     * input. This is needed for Django to understand what was selected not
     * for the actual view of the interface. The actual checkbox population in
     * the interface is done automatically by flat ui's js files.
     */
    $('.checkbox-toggle input').each(function(ind, item) {
       $(item).change(function(){
           var label = $("label[for='"+$(item).attr('id')+"']")[1];
           var label_class = $(label).attr('class');
           var label_last = label_class.substr(label_class.lastIndexOf(' ') + 1);

           if(label_last === "checked"){
               $(item).val(true);
           } else {
               $(item).val(false);
           }
       });
    });
    $("[data-toggle='tooltip']").tooltip('hide');

    $("#id_specific_interests").select2({
        placeholder: "Select what you care about",
        allowClear: true,
        width: "100%"
    });
    $(".tooltip").addClass(function() {
        if ($(this).prev().attr("data-tooltip-style")) {
        return "tooltip-" + $(this).prev().attr("data-tooltip-style");
      }
    });
});

