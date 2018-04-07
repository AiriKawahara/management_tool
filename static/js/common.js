$(function(){
  // datepicker設定値
  $("#deadline_input").flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    minDate: getDate(),
    defaultDate: getDate()
  });

  $("#start_date_input").flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    defaultDate: getDate()
  });

  $("#end_date_input").flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    defaultDate: getDate(7)
  });

  $('#everyday').click(function() {
    $('#deadline_input').val('2099-12-31');
  });

  $('#reset').click(function() {
    $('#deadline_input').val(getDate());
  });

  setInputValue();
});

/**
 * 今日からdays日後の日付を取得する。
 */
function getDate(days = 0) {
  const date = new Date()
  date.setDate(date.getDate() + days);
  const year = date.getFullYear();
  const month = ('0' + (date.getMonth() + 1)).slice(-2);
  const day = ('0' + date.getDate()).slice(-2);
  const today = year + '-' + month + '-' + day;
  return today;
}

/**
 * 検索ボックスにURLパラメータの値をセットする。
 */
function setInputValue() {
  // URLパラメータを取得
  var arg = new Object;
  var pair = location.search.substring(1).split('&');
  for(var i = 0; pair[i]; i++) {
    var kv = pair[i].split('=');
    arg[kv[0]]=kv[1];
  }

  // 検索ボックスにURLパラメータの値をセット
  if (arg.start_date_input) {
    arg.start_date_input = decodeURI(arg.start_date_input);
    $('#start_date_input').val(arg.start_date_input);
  }

  if (arg.end_date_input) {
    arg.end_date_input = decodeURI(arg.end_date_input);
    $('#end_date_input').val(arg.end_date_input);
  }
}
