$(function() {
  // メモ帳を改行させるための処理
  $('.content').each(function(elem) {
    var content = $(this).text();
    $(this).text('');
    $(this).append(content);
  });

  // 編集ボタン押下時
  $('.edit').click(function() {
    controlDialog($(this), 'edit');
  });
});

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
  var cwDelete = $('.delete-dialog').outerWidth();
  var chDelete = $('.delete-dialog').outerHeight();

  //センタリングを実行する
  $('.edit-dialog').css({
    'left': ((w - cwEdit) / 2) + 'px',
    'top': ((h - chEdit) / 2) + 'px'
  });

  $('.complete-dialog').css({
    'left': ((w - cwComplete) / 2) + 'px',
    'top': ((h - chComplete) / 2) + 'px'
  });

  $('.delete-dialog').css({
    'left': ((w - cwDelete) / 2) + 'px',
    'top': ((h - chDelete) / 2) + 'px'
  });
}

/**
 * タスク完了ダイアログの表示/非表示制御を行う。
 * @param {object} $elem 押下されたボタンのjQueryオブジェクト
 * @param {string} type  表示するダイアログの種類
 */
function controlDialog($elem, type) {
  var sort    = $elem.data('sort');
  var content = $elem.data('content');

  console.log(content);

  // キーボード操作などにより、オーバーレイが多重起動するのを防止する
  $elem.blur();  // ボタンからフォーカスを外す
  if ($('#overlay')[0]) return false;   // 新しくモーダルウィンドウを起動しない(防止策1)

  //オーバーレイを出現させる
  $('body').append('<div id="overlay"></div>');
  $('#overlay').show();

  // タスク情報をセット
  if (type == 'edit') {
    $('.edit-dialog #sort').val(sort);
    $('.edit-dialog #dialog_content').val(content);
  } else {
    // $(`.${type}-dialog #task_name`).val(taskName);
    // $(`.${type}-dialog #deadline`).val(deadline);
  }

  centeringDialogSyncer();
  $(`.${type}-dialog`).show();

  // ダイアログの背景を押下したらダイアログを閉じる
  $('#overlay').unbind().click(function() {
    $(`.${type}-dialog, #overlay`).hide();
    $('#overlay').remove();
  });

  // 削除ダイアログの「いいえ」ボタンを押下したらダイアログを閉じる
  $('.dialog-close').click(function() {
    $(`.${type}-dialog, #overlay`).hide();
    $('#overlay').remove();
  });
}
