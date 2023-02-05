#!/usr/bin/env python
import validators
from telegram import Update
from telegram.ext import ContextTypes
bad_url_text = "Bad url. Please use next format: http://example.com"


def required_argument(fn):
    def wrapper(bot: Update, context: ContextTypes.DEFAULT_TYPE):
        if int(len(context.args)) == 0:
            bot.message.reply_text(bad_url_text)
            return False
        return fn(bot, context)
    return wrapper


def valid_url(fn):
    def wrapper(bot: Update, context: ContextTypes.DEFAULT_TYPE):
        if not validators.url(context.args[0], public=True):
            bot.message.reply_text(bad_url_text)
            return False
        return fn(bot, context)
    return wrapper
