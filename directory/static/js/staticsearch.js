$(function() {
  $("[data-staticsearchbox]").typeahead({
    hint: true,
    highlight: true,
    minLength: 1
  }, {
    name: 'staticsearch',
    displayKey: 'value',
    source: function findMatches(q, cb) {
      var matches = [];

      q = q.toLowerCase();
      $('[data-staticsearchable]').each(function() {
        var text = $(this).text();
        if (text.toLowerCase().indexOf(q) != -1)
          matches.push({value: text});
      });

      cb(matches);
    }
  });
});
