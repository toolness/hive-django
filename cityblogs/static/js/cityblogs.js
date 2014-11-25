$(function() {
  $('[data-cityblogs-splat-url]').each(function() {
    var $this = $(this);
    var url = $this.attr('data-cityblogs-splat-url');
    $this.hide();
    $.get(url, function(html, textStatus, jqXHR) {
      $this.html(html);
      $this.fadeIn();
    });
  });
});
