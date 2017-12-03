# -*- coding: utf-8 -*-

from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
# for env
import os
# for regexp
import re
# for https requests
import requests

from pocket import Pocket, PocketException

# pocket key
CONSUMER_KEY = os.getenv('CONSUMER_KEY', 'consumer_key')
POCKET_ACCESS_TOKEN = os.getenv('POCKET_ACCESS_TOKEN', 'pocket_access_token')

pocket_instance = Pocket(consumer_key = CONSUMER_KEY, access_token = POCKET_ACCESS_TOKEN)

def main():
    bot = Bot()
    bot.run()

@listen_to('pocket-list')
def list_tasks(message):
    print(POCKET_ACCESS_TOKEN)
    try:
        data = pocket_instance.retrieve()
        articles = data['list'].values()
        message.send('保存されている記事のリストです')
        for article in articles:
            content = f'*{article["given_title"]}*\n' if article['given_title'] else ''
            content += '```\n'
            content += f'{article["excerpt"]}\n' if 'excerpt' in article.keys() else ''
            content += f'{article["given_url"]}\n```'

            message.send(content)
    except PocketException as e:
        message.send(e.message)

@listen_to('pocket-add')
def add_tasks(message):
    data = re.search(r'\s\<(http.+)\>\s*(.*)', message.body['text'])
    if data is None:
        message.send('`pocked-add URL (タイトル)`という形式にしてください。')
        return

    matched_url = data.group(1)
    matched_title = data.group(2)

    if matched_url is None:
        message.send('`pocked-add URL (タイトル)`という形式にしてください。')
        return

    url = matched_url
    title = matched_title if matched_title is not None else ''

    pocket_instance.add(url, title)
    message.send(
        'Pocketに追加しました！\n```\n' +
        f'タイトル : {title}\n' +
        f'URL : {url}\n```'
    )

@listen_to('pocket-help')
def help_pocket(message):
    message.send(
        '-使い方-\n```\n' +
        '# Pocketの記事一覧を表示する*\n' +
        'pocket-list\n\n' +
        '# Pocketに記事を登録する\n' +
        'pocket-add URL タイトル\n\n' +
        '# Pocketのヘルプを表示する\n' +
        'pocket-help\n```'
    )

if __name__ == "__main__":
    print('start slackbot')
    main()
