$(".item").click(function () {
  $(".selected").remove();
  $("<div class='selected'>Selected</div>").prependTo(this);
});