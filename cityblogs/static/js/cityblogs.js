$(function() {
  $('[data-cityblogs-splat-url]').each(function() {
    var $this = $(this);
    var url = $this.attr('data-cityblogs-splat-url');
    $.get(url, function(html, textStatus, jqXHR) {
      $this.html(html);
    });
  });
});
