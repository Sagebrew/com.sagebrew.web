  $(document).ready(function() {

   var docHeight = $(window).height();
   var footerHeight = $('#sb_footer').height();
   var footerTop = $('#sb_footer').position().top + footerHeight;

   if (footerTop < docHeight) {
    $('#sb_footer').css('margin-top', 10+ (docHeight - footerTop) + 'px');
   }
  });