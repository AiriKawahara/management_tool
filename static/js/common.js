$(function() {
  // datepicker設定値
  $('#deadline_input').flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    minDate: getDate(),
    defaultDate: getDate()
  });

  $('#start_date_input').flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    defaultDate: getDate()
  });

  $('#end_date_input').flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    defaultDate: getDate(7)
  });

  $('#complete_date').flatpickr({
    enableTime: false,
    dateFormat: "Y-m-d",
    maxDate: getDate(),
    defaultDate: getDate()
  });

  $('#everyday').click(function() {
    $('#deadline_input').val('2099-12-31');
  });

  $('#reset').click(function() {
    $('#deadline_input').val(getDate());
  });

  // 編集ボタン押下時
  $('.edit').click(function() {
    controlDialog($(this), 'edit');
  });

  // 完了ボタン押下時
  $('.complete').click(function() {
    controlDialog($(this), 'complete');
  });

  // リサイズされたらダイアログのセンタリングを行う
  $(window).resize(centeringDialogSyncer);

  setInputValue();
});

/**
 * 今日からdays日後の日付を取得する。
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

/**
 * ダイアログをセンタリングする。
 */
function centeringDialogSyncer() {
  //画面(ウィンドウ)の幅、高さを取得
  var w = $(window).width();
  var h = $(window).height();
  var cwEdit = $('.edit-dialog').outerWidth();
  var chEdit = $('.edit-dialog').outerHeight();
  var cwComplete = $('.complete-dialog').outerWidth();
  var chComplete = $('.complete-dialog').outerHeight();

  //センタリングを実行する
  $('.edit-dialog').css({
    'left': ((w - cwEdit) / 2) + 'px',
    'top': ((h - chEdit) / 2) + 'px'
  });

  $('.complete-dialog').css({
    'left': ((w - cwComplete) / 2) + 'px',
    'top': ((h - chComplete) / 2) + 'px'
  });
}

/**
 * タスク完了ダイアログの表示/非表示制御を行う。
 * @param {object} $elem 押下されたボタンのjQueryオブジェクト
 * @param {string} type  タスク編集かタスク完了か
 */
function controlDialog($elem, type) {
  var taskName = $elem.data('name');
  var deadline = $elem.data('deadline');

  //キーボード操作などにより、オーバーレイが多重起動するのを防止する
  $elem.blur();  //ボタンからフォーカスを外す
  if($('#overlay')[0]) return false;   //新しくモーダルウィンドウを起動しない (防止策1)

  //オーバーレイを出現させる
  $('body').append('<div id="overlay"></div>');
  $('#overlay').show();

  // タスク情報をセット
  $(`.${type}-dialog #task_name`).val(taskName);
  $(`.${type}-dialog #deadline`).val(deadline);

  centeringDialogSyncer();
  $(`.${type}-dialog`).show();

  // ダイアログの背景を押下したらダイアログを閉じる
  $('#overlay').unbind().click(function() {
    $(`.${type}-dialog, #overlay`).hide();
    $('#overlay').remove();
  });
}
