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
    google.charts.setOnLoadCallback(getFigure);
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
function getFigure() {
  var data = {
    "figure_start_date": $('#figure_start_date').val(),
    "figure_end_date": $('#figure_end_date').val()
  }

  $.ajax({
    type: 'GET',
    url: '/get_figure',
    data: data,
    timeout: 10000
  })
  .done(function(response) {
    if (response.length == 0) {
      location.reload();
      return;
    }

    var graphData = [];
    response.forEach(function(val) {
      graphData.push(
        [
          val.figure_date,
          val.weight,
          val.fat,
          val.right_thickness,
          val.left_thickness
        ]
      )
    });

    drawFigureGraph(graphData);

  }).fail(function(xhr, textStatus, errorThrown) {
    alert('エラーが発生しました。');
    console.log(textStatus);
    console.log(xhr);
    console.log(errorThrown);
  });
}

/**
 * グラフを描画する。
 * 参考URL：https://developers.google.com/chart/interactive/docs/gallery/linechart
 * @param {array} graphData グラフ描画用配列
 */
function drawFigureGraph(graphData) {
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'X');
  data.addColumn('number', '体重 (kg)');
  data.addColumn('number', '体脂肪率 (%)');
  data.addColumn('number', '右太もも (cm)');
  data.addColumn('number', '左太もも (cm)');

  data.addRows(graphData);

  var options = {
    hAxis: {
      logScale: true
    },
    vAxis: {
      logScale: false
    },
    colors: ['#a52714', '#097138']
  };

  var chart = new google.visualization.LineChart(document.getElementById('chart_area'));
  chart.draw(data, options);
}