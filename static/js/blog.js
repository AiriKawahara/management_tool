$(function() {
  $('#month').flatpickr({
    enableTime: false,
    dateFormat: "Y/m",
    maxDate: getDate(),
    defaultDate: getDate()
  });
});
