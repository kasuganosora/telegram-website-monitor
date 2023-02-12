# telegram-website-monitor

Telegram bot to check that the page is changed or domain can register.

You can found bot here: [https://t.me/website_monitor_bot](https://t.me/website_monitor_bot)

## Install

    $ virtualenv -p python3 venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    $ deactivate

## Run

    $ source venv/bin/activate
    $ python3 main.py

## Cron

Add to cron job with file `cron.py`

example:

    $ crontab -e
    */20 * * * * /home/user/bot/telegram-website-monitor/cron.sh > /tmp/1.txt  


## Commands  

```
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
```

## License  

bese on [ Kuznetsov Aleksey <crusat@yandex.ru>] https://github.com/crusat/telegram-website-monitor  
License: MIT  
Created: 2023/2/25  
