$(function() {
  $('.expand-icon').click(function() {
    var hasClassOpen = $(this).hasClass('open');
    var targetElem   = $(this).parent().next('div');
    if (hasClassOpen) {
      $(this).toggleClass('open');
      $(this).text('expand_less');
      $(targetElem).hide();
    } else {
      $(this).toggleClass('open');
      $(this).text('expand_more');
      $(targetElem).show();
    }
  });
});