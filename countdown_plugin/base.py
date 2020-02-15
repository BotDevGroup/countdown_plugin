# -*- coding: utf-8 -*-

from marvinbot.utils import localized_date, get_message
from marvinbot.handlers import CommandHandler, CallbackQueryHandler
from marvinbot.plugins import Plugin
from marvinbot.models import User

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import logging
import requests
import traceback

log = logging.getLogger(__name__)


class CountdownPlugin(Plugin):
    def __init__(self):
        super(CountdownPlugin, self).__init__('countdown_rae_plugin')
        self.bot = None

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
            'base_url': 'https://yourcountdown.to'
        }

    def configure(self, config):
        self.config = config
        pass

    def setup_handlers(self, adapter):
        self.bot = adapter.bot
        self.add_handler(CommandHandler('countdown', self.on_countdown_command, command_description='Search the countdown of series or movies. https://yourcountdown.io'))

    def setup_schedules(self, adapter):
        pass

    def html_parse(self, response):
        def strfdelta(tdelta):
            (h, r) = divmod(tdelta.seconds, 3600)
            (m, s) = divmod(r, 60)
            d = tdelta.days if tdelta.days else 0
            return [d, h, m, s]

        date_format = '%Y-%m-%d %H:%M:%S'    
        response.encoding = "utf-8"
        html_soup = BeautifulSoup(response.text, 'html.parser')
       
        results = []

        for item in html_soup.find_all('div', class_='countdown-item'):
            countdown = item.find('div', class_='countdown')
            if not countdown['data-timezone']: countdown['data-timezone'] = "0"
            future = datetime.strptime(countdown['data-date'], date_format) - timedelta(hours = float(countdown['data-timezone']))
            present = datetime.now()
            difference = future - present

            new = {}
            new['name'] = item.h4.text
            new['title'] = item.p.text
            new['img'] = "{}{}".format(self.config.get('base_url'), item.find('a', class_='countdown-block')['data-src'])
            new['countdown'] = "{} *DAYS* {} *HOURS* {} *MINS*".format(*strfdelta(difference))
            new['display'] = False if difference.days < 0 else True
            results.append(new)

        return results[:3]

    def http(self, search=""):
        with requests.Session() as s:
            url = "{}/everything?search={}".format(self.config.get('base_url'), search)
            response = s.get(url)
            return self.html_parse(response)

    def on_countdown_command(self, update, *args, **kwargs):
        message = get_message(update)
        msg = ""

        try:
            cmd_args = message.text.split(" ")
            if len(cmd_args) > 1:
                search = " ".join(cmd_args[1:])
                results = self.http(search = search)

                if len(results) > 0:
                    for item in results:
                        msg = "*Name:* {}\n*Title:* {}\n{}".format(item['name'], item['title'], item['countdown']) if item['display'] else "Go watch it!"
                        self.adapter.bot.sendPhoto(chat_id=message.chat_id, photo=item['img'], caption=msg, parse_mode='Markdown')
                    return
                else:
                    msg = "❌ Found 0 countdown."
            else:
                msg = "‼️ Use: /countdown <serie|movie>"
        except Exception as err:
            log.error("Countdown error: {}".format(err))
            msg = "❌ Unable to fetch countdown information."
            traceback.print_exc()

        self.adapter.bot.sendMessage(chat_id=message.chat_id, text=msg, parse_mode='Markdown', disable_web_page_preview = True)
    
          
