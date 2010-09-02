jQuery(".jpoker_chat_input > input").live("focus", function() {
  if (jQuery(this).val() == 'chat here') {
    jQuery(this).val('');
  }
});

jQuery(".jpoker_chat_input > input").live("blur", function() {
  if (jQuery(this).val() == '') {
    jQuery(this).val('chat here');
  }
});