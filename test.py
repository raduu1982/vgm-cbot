def show_crawlers_to_search(self, bot, update, user_data):
    app = user_data.get('app')

    buttons = []

    def make_button(i, url):
        return '%d - %s' % (i + 1, urlparse(url).hostname)

    # end def
    for i in range(1, len(app.crawler_links) + 1, 2):
        buttons += [[
            make_button(i - 1, app.crawler_links[i - 1]),
            make_button(i, app.crawler_links[i]) if i < len(
                app.crawler_links) else '',
        ]]
    # end for

    update.message.reply_text(
        'Choose where to search for your novel, \n'
        'or send /skip to search everywhere.',
        reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True),
    )
    return 'handle_crawler_to_search'
# end def