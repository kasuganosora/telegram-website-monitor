#!/usr/bin/env python
from telegram.ext import Application, CommandHandler,ContextTypes
from settings import TELEGRAM_API_KEY, BOTAN_TOKEN
from data import Website
import requests
from decorators import required_argument, valid_url
from telegram import ForceReply, Update,Bot
import checker

help_text = """
The bot ensures that your website was always online. In the case of content changes, the bot will tell you that you need to pay attention to the site. The website is checked for availability every 5 minutes.

Commands:

/help - Help
/list - Show yours added urls
/add <url> - Add new url for monitoring
/del <url> - Remove exist url
/test <url> - Test current status code for url right now

Url format is http[s]://host.zone/path?querystring
For example:

/test https://crusat.ru

For any issues visit:https://github.com/kasuganosora/telegram-website-monitor/issues

Contact author: @kasuganosora
base on: https://github.com/crusat/telegram-website-monitor
"""


async def start(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot.message.reply_text("Hello!\nThis is telegram bot to check that the url content change.\n%s" % help_text)


async def show_help(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot.message.reply_text("%s" % help_text)

@required_argument
@valid_url
async def add(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    print('add')
    print(args[0])
    url = args[0]
    param = ''
    if len(args) > 1:
        param = args[1]
    print(url + '\t' + param)

    website_count = (Website.select().where((Website.chat_id == bot.effective_message.chat_id) & (Website.url == url)).count())
    print(website_count)
    if website_count == 0:
        website = Website(chat_id=bot.effective_message.chat_id, url=url, method='check_content', param=param)
        print('ok1')
        website.save(force_insert=True)
        print('ok2')
        await bot.message.reply_text("Added %s" % url)
        print('ok3')
    else:
        await bot.message.reply_text("Website %s already exists" % url)
    print('end')


@required_argument
async def delete(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    url = args[0].lower()
    website = Website.get((Website.chat_id == bot.effective_message.chat_id) & (Website.url == url))
    if website:
        website.delete_instance()
        await bot.message.reply_text("Deleted %s" % url)
    else:
        await bot.message.reply_text("Website %s is not exists" % url)


async def url_list(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    websites = (Website.select().where(Website.chat_id == bot.effective_message.chat_id))
    out = ''
    for website in websites:
        out += "%s\n" % (website.url)
    if out == '':
        await bot.message.reply_text("List empty")
    else:
        await bot.message.reply_text(out)

@required_argument
@valid_url
async def test(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0]
    param = ''

    if len(context.args) > 1:
        param = context.args[1]

    try:
        result = checker.check_content(url, param)
    except:
        if len(param) == 0:
            await bot.message.reply_text("param is error")
            return
    
    if result['fetch'] is False:
        await bot.message.reply_text("fetch %s is error" % url)
        return
    
    if len(param) == 0:
        await bot.message.reply_text("fetch %s is ok, status code %d" % url, result['status_code'])
    else:
        await bot.message.reply_text("fetch %s is ok, status code %d, match %s" % url, result['status_code'], result['match_content'])

app = Application.builder().token(TELEGRAM_API_KEY).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("del", delete))
app.add_handler(CommandHandler("list", url_list))
app.add_handler(CommandHandler("test", test))
app.add_handler(CommandHandler("help", show_help))

app.run_polling()
