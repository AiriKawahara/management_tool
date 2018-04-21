/**
 * 今日からdays日後の日付を取得する。
 * @param {number} days
 */
function getDate(days = 0) {
  var date = new Date()
  date.setDate(date.getDate() + days);
  var year = date.getFullYear();
  var month = ('0' + (date.getMonth() + 1)).slice(-2);
  var day = ('0' + date.getDate()).slice(-2);
  var today = year + '-' + month + '-' + day;
  return today;
}