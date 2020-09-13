def test_send_message_with_inlinemarkup(self):
    text = 'CI Test Message'
    tb = telebot.TeleBot(TOKEN)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Google", url="http://www.google.com"))
    markup.add(types.InlineKeyboardButton("Yahoo", url="http://www.yahoo.com"))
    ret_msg = tb.send_message(CHAT_ID, text, disable_notification=True, reply_markup=markup)
    assert ret_msg.message_id