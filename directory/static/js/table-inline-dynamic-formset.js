$(function() {
  function makeFormsetDynamic(form, prefix) {
    function getInput(name) {
      return form.find('input[name="' + prefix + name + '"]');
    }

    function makeNextRow() {
      var row = blankRow.clone();
      var newId = blankId + 1;
      var namePrefix = prefix + blankId;
      var newNamePrefix = prefix + newId;

      row.find('[name^="' + namePrefix + '"]')
        .each(function() {
          var oldName = $(this).attr('name');
          var suffix = oldName.slice(namePrefix.length);
          var newName = newNamePrefix + suffix;
          $(this).attr('name', newName);

          row.find('[id$="' + oldName + '"]')
            .each(function() {
              var idPrefix = $(this).attr('id').slice(0, -oldName.length);
              $(this).attr('id', idPrefix + newName);
            });
        });
      return row;
    }

    var totalForms = getInput('TOTAL_FORMS');
    var numTotalForms = parseInt(totalForms.attr('data-val') || 
                                 totalForms.val());
    var numInitialForms = parseInt(getInput('INITIAL_FORMS').val());
    var blankId = numTotalForms - 1;
    var blankRow = getInput(blankId + '-DELETE').parents('tr');

    if (numTotalForms - numInitialForms == 0 ||
        blankRow.length != 1 ||
        !$.contains(form[0], blankRow[0]))
      return;

    var newBlankRow = makeNextRow();

    blankRow.one('focus', 'input, select, textarea', function() {
      totalForms.attr('data-val', numTotalForms + 1);
      blankRow.after(newBlankRow);
      newBlankRow.hide().fadeIn(function() {
        makeFormsetDynamic(form, prefix);
      });
    });
  }

  $('input[name$=TOTAL_FORMS]').each(function() {
    var prefix = $(this).attr('name').split('TOTAL_FORMS')[0];
    var form = $(this).parents('form');

    makeFormsetDynamic(form, prefix);
  });

  $(document.body).on('submit', 'form', function(e) {
    // Reflect data-val attributes to values. We need to do this in
    // order to prevent browsers like Firefox from remembering the
    // changed value of a hidden form management field across page
    // reloads.
    $('[data-val]', this).each(function() {
      $(this).val($(this).attr('data-val'));
    });
  });
});
