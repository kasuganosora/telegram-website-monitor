#!/usr/bin/env python
import telegram
from settings import TELEGRAM_API_KEY
from data import Website
import checker
import asyncio


bot = telegram.Bot(token=TELEGRAM_API_KEY)

async def main():
    websites = (Website.select())

    for website in websites:
        url = website.url
        method = website.method

        try:
            if method == 'check_content':
                param = website.param
                result = checker.content_check(url, param)
                if result['fetch'] is True and website.last != result['match_hash']:
                    website.last = result['match_hash']
                    website.save()

                    if len(website.param) > 0:
                        await bot.sendMessage(chat_id=website.chat_id,
                                        text="Content changed for %s. Current is %s." % (website.url, result['match_content']))
                    else:
                        await bot.sendMessage(chat_id=website.chat_id,
                                        text="Content changed for %s." % website.url)
        except Exception as e:
            print('Error for url %s' % url)
            print(e)

if __name__ == '__main__':
    asyncio.run(main())