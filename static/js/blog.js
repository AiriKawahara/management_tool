$(function() {
  $('#month, #blog_end_month').flatpickr({
    enableTime: false,
    dateFormat: 'Y/m',
    maxDate: getDate(),
    defaultDate: getDate()
  });

  $('#blog_start_month').flatpickr({
    enableTime: false,
    dateFormat: 'Y/m',
    defaultDate: '2018/01'
  });

  // 検索ボタン押下時処理
  $('.search').click(function() {
    $('#chart_area').height('500px');
    google.charts.load('current', {packages: ['corechart', 'line']});
    google.charts.setOnLoadCallback(getBlog);
  });
});

/**
 * ブログデータを取得する。
 */
function getBlog() {
  var data = {
    "blog_start_month": $('#blog_start_month').val(),
    "blog_end_month": $('#blog_end_month').val()
  }

  $.ajax({
    type: 'GET',
    url: '/get_blog',
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
          val.month,
          val.other_user_access,
          val.visitors_count,
          val.posts_count
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
  data.addColumn('number', 'アクセス数');
  data.addColumn('number', '訪問者数');
  data.addColumn('number', '投稿数');

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
