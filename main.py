#!/usr/bin/env python
from telegram.ext import Application, CommandHandler,ContextTypes
from settings import TELEGRAM_API_KEY
from data import Website, Domain
import requests
from decorators import required_argument, valid_url
from telegram import Update
import checker

help_text = """
The bot can check that the url content change and domain can be registered.

Commands:

/help - Help
/list - Show yours added urls
/add <url> - Add new url for monitoring
/del <url> - Remove exist url
/test <url> - Test current status code for url right now

Url format is http[s]://host.zone/path?querystring
For example:

/test https://google.com

check domain can be registered
/list_domains - Show yours added domains
/add_domain <domain> - Add new domain for monitoring
/del_domain <domain> - Remove exist domain


Contact author: @kasuganosora
https://github.com/kasuganosora/telegram-website-monitor
"""


async def start(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot.message.reply_text("Hello!\nThe bot can check that the url content change and domain can be registered.\n%s" % help_text)


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
        # check can fetch
        try:
            result = checker.content_check(url, param)
            if result['fetch'] is False:
                await bot.message.reply_text("Can't fetch %s" % url)
                return
            website = Website(chat_id=bot.effective_message.chat_id, url=url, method='check_content', param=param, last=result['match_hash'])
            website.save(force_insert=True)
        except Exception as e:
            await bot.message.reply_text('error %s' % e)
            return
        
        await bot.message.reply_text("Added %s" % url)
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
        result = checker.content_check(url, param)
        if result['fetch'] is False:
            await bot.message.reply_text("fetch %s is error" % url)
            return
        
        if len(param) == 0:
            await bot.message.reply_text("fetch %s is ok, status code %d" % (url, result['status_code']))
        else:
            await bot.message.reply_text("fetch %s is ok, status code %d, match %s" % (url, result['status_code'], result['match_content']))
    except Exception as e:
        await bot.message.reply_text('error %s' % e)


async def list_domains(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    domains = (Domain.select().where(Domain.chat_id == bot.effective_message.chat_id))
    out = ''
    for domain in domains:
        status = 'registered'
        if domain.last == 'true':
            status = 'unregistered'
        out += "%s\t%s\n" % (domain.domain, status)
    
    if out == '':
        await bot.message.reply_text("List empty")
    else:
        await bot.message.reply_text(out)

async def add_domain(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.args[0]
    domain_count = (Domain.select().where((Domain.chat_id == bot.effective_message.chat_id) & (Domain.domain == d)).count())
    if domain_count == 0:
        # check domain current status
        status = 'false'
        if checker.check_domain_can_reg(d):
            status = 'true'
        record = Domain(chat_id=bot.effective_message.chat_id, domain=d, last=status)
        record.save(force_insert=True)

        await bot.message.reply_text("Added %s" % d)

    else:
        await bot.message.reply_text("Domain %s already exists" % d)


async def delete_domain(bot: Update, context: ContextTypes.DEFAULT_TYPE):
    d = context.args[0]
    domain = Domain.get((Domain.chat_id == bot.effective_message.chat_id) & (Domain.domain == d))
    if domain:
        domain.delete_instance()
        await bot.message.reply_text("Deleted %s" % d)
    else:
        await bot.message.reply_text("Domain %s is not exists" % d)

app = Application.builder().token(TELEGRAM_API_KEY).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("del", delete))
app.add_handler(CommandHandler("list", url_list))
app.add_handler(CommandHandler("test", test))
app.add_handler(CommandHandler("help", show_help))
app.add_handler(CommandHandler("list_domains", list_domains))
app.add_handler(CommandHandler("add_domain", add_domain))
app.add_handler(CommandHandler("del_domain", delete_domain))


print('Telegram bot started')
app.run_polling()
