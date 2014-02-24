$('body').on('click', '[data-submit-form-onclick]', function() {
  var form = $('form', this);
  if (!form.length) return alert('ERROR: No form found in ' +
                                 'data-submit-form-onclick element!');
  form.submit();
  return false;
});
