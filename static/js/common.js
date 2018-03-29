$(function(){
  // datepicker設定値
  const today = getToday();
  $(".flatpickr").flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    maxDate: today,
    defaultDate: today
  });
});

/**
 * 今日の日付を取得する。
 */
function getToday() {
  const date = new Date();
  const year = date.getFullYear();
  const month = ('0' + (date.getMonth() + 1)).slice(-2);
  const day = ('0' + date.getDate()).slice(-2);
  const today = year + '-' + month + '-' + day;
  return today;
}
