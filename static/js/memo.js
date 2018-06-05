$(function() {
  // メモ帳を改行させるための処理
  $('.content').each(function(elem) {
    var content = $(this).text();
    $(this).text('');
    $(this).append(content);
  });
});