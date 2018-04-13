$(function() {
  $('#figure_date').flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    maxDate: getDate(),
    defaultDate: getDate()
  });

  $('#figure_start_date').flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    defaultDate: getDate(-14)
  });

  $('#figure_end_date').flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    defaultDate: getDate()
  });

  // 検索ボタン押下時処理
  $('.search').click(function() {
    $('#chart_area').width('900px');
    $('#chart_area').height('500px');
    google.charts.load('current', {packages: ['corechart', 'line']});
    google.charts.setOnLoadCallback(drawLogScales);
  });
});

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

/**
 * 体型管理データを取得する。
 */
function get_figure() {
  var data = {
    "figure_start_date": $('#figure_start_date').val(),
    "figure_end_date": $('#figure_end_date').val()
  }

  // $.ajax({
  //   type: 'GET',
  //   url: '/get_figure',
  //   data: data,
  //   timeout: 10000
  // })
  // .done(function(response) {
  //   console.log(response);
    return [
      [0, 0, 0],    [1, 10, 5],   [2, 23, 15],  [3, 17, 9],   [4, 18, 10],  [5, 9, 5],
      [6, 11, 3],   [7, 27, 19],  [8, 33, 25],  [9, 40, 32],  [10, 32, 24], [11, 35, 27],
      [12, 30, 22], [13, 40, 32], [14, 42, 34], [15, 47, 39], [16, 44, 36], [17, 48, 40],
      [18, 52, 44], [19, 54, 46], [20, 42, 34], [21, 55, 47], [22, 56, 48], [23, 57, 49],
      [24, 60, 52], [25, 50, 42], [26, 52, 44], [27, 51, 43], [28, 49, 41], [29, 53, 45],
      [30, 55, 47], [31, 60, 52], [32, 61, 53], [33, 59, 51], [34, 62, 54], [35, 65, 57],
      [36, 62, 54], [37, 58, 50], [38, 55, 47], [39, 61, 53], [40, 64, 56], [41, 65, 57],
      [42, 63, 55], [43, 66, 58], [44, 67, 59], [45, 69, 61], [46, 69, 61], [47, 70, 62],
      [48, 72, 64], [49, 68, 60], [50, 66, 58], [51, 65, 57], [52, 67, 59], [53, 70, 62],
      [54, 71, 63], [55, 72, 64], [56, 73, 65], [57, 75, 67], [58, 70, 62], [59, 68, 60],
      [60, 64, 56], [61, 60, 52], [62, 65, 57], [63, 67, 59], [64, 68, 60], [65, 69, 61],
      [66, 70, 62], [67, 72, 64], [68, 75, 67], [69, 80, 72]
    ]
  // }).fail(function(xhr, textStatus, errorThrown) {
  //   alert('エラーが発生しました。');
  //   console.log(textStatus);
  //   console.log(xhr);
  //   console.log(errorThrown);
  // });
}

/**
 * グラフを描画する。
 * 参考URL：https://developers.google.com/chart/interactive/docs/gallery/linechart
 */
function drawLogScales() {
  var data = new google.visualization.DataTable();
  data.addColumn('number', 'X');
  data.addColumn('number', 'Dogs');
  data.addColumn('number', 'Cats');

  data.addRows(get_figure());

  var options = {
    hAxis: {
      title: 'Time',
      logScale: true
    },
    vAxis: {
      title: 'Popularity',
      logScale: false
    },
    colors: ['#a52714', '#097138']
  };

  var chart = new google.visualization.LineChart(document.getElementById('chart_area'));
  chart.draw(data, options);
}