$(function() {
  // datepicker設定値
  $('#deadline_input').flatpickr({
    enableTime: false,
    dateFormat: 'Y-m-d',
    minDate: getDate(),
    defaultDate: getDate()
  });

  $('#start_date_input').flatpickr({
    enableTime: false,
    dateFormat: 'Y-m-d',
    defaultDate: getDate()
  });

  $('#end_date_input').flatpickr({
    enableTime: false,
    dateFormat: 'Y-m-d',
    defaultDate: getDate(7)
  });

  $('#complete_date').flatpickr({
    enableTime: false,
    dateFormat: 'Y-m-d',
    maxDate: getDate(),
    defaultDate: getDate()
  });

  $('#everyday').click(function() {
    $('#deadline_input').val('2099-12-31');
    $('#deadline_input').flatpickr({
      defaultDate: '2099-12-31'
    });
  });

  $('#reset').click(function() {
    $('#deadline_input').val(getDate());
    $('#deadline_input').flatpickr({
      defaultDate: getDate()
    });
  });

  $('#everyday_edit').click(function() {
    $('#new_deadline').val('2099-12-31');
    $('#new_deadline').flatpickr({
      defaultDate: '2099-12-31'
    });
  });

  $('#reset_edit').click(function() {
    $('#new_deadline').val(getDate());
    $('#new_deadline').flatpickr({
      defaultDate: getDate()
    });
  });

  // 要素の開閉
  $('.expand-icon').click(function() {
    var hasClassOpen = $(this).hasClass('open');
    var targetElem   = $(this).parent().next('table,span,form,div');

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

  // 編集ボタン押下時
  $('.edit').click(function() {
    controlDialog($(this), 'edit');
  });

  // 完了ボタン押下時
  $('.complete').click(function() {
    controlDialog($(this), 'complete');
  });

  // 削除ボタン押下時
  $('.delete').click(function() {
    controlDialog($(this), 'delete');
  });

  // リサイズされたらダイアログのセンタリングを行う
  $(window).resize(centeringDialogSyncer);

  setInputValue();
});

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
  var taskName = $elem.data('name');
  var deadline = $elem.data('deadline');

  // キーボード操作などにより、オーバーレイが多重起動するのを防止する
  $elem.blur();  // ボタンからフォーカスを外す
  if($('#overlay')[0]) return false;   // 新しくモーダルウィンドウを起動しない (防止策1)

  //オーバーレイを出現させる
  $('body').append('<div id="overlay"></div>');
  $('#overlay').show();

  // タスク情報をセット
  if (type == 'edit') {
    $('.edit-dialog #old_task_name').val(taskName);
    $('.edit-dialog #new_task_name').val(taskName);
    $('.edit-dialog #old_deadline').val(deadline);
    $('.edit-dialog #new_deadline').val(deadline);

    $('#new_deadline').flatpickr({
      enableTime: false,
      dateFormat: "Y-m-d",
      defaultDate: deadline
    });
  } else {
    $(`.${type}-dialog #task_name`).val(taskName);
    $(`.${type}-dialog #deadline`).val(deadline);
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
