from bs4 import BeautifulSoup as bs

import requests
import telebot
import config
import json
import re

bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode='MARKDOWN')

###################################MessageHandler######################################

#! Bot's start message
@bot.message_handler(commands=['start'])
def starting(message):
    bot.send_message(
            message.chat.id,
            'Greetings, I can show you some youtube videos!\n' +
            'I was invented to search youtube videos in telegram\n' + 
            'With me you can do it independent and safe\n' +
            'Press /help for more information'
            )

#! Bot's help message
@bot.message_handler(commands=['help'])
def helping(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Message the developer', url=config.developer_url
                )
            )
    keyboard.row(
            telebot.types.InlineKeyboardButton('New Channel', callback_data='new_channel'),
            telebot.types.InlineKeyboardButton('Channels', callback_data='channel_list')
            )
    bot.send_message(
            message.chat.id,
            'To add new channel to the list of channels press:\n' +
            '`New channels` \n' +
            'Then type a full link (example https://notyoutube.org/channel/UCdKuE7a2QZeHPhDntXVZ91w) \n' +
            'You should use links from notyoutube.org for \n' +
            'maximum safety (and not for kapcha (i hate it))\n' +
            'To get some urls to the channels in list press: \n' +
            '`Channels`',
            reply_markup=keyboard
            )

@bot.message_handler(func=lambda m: m.text.startswith('https://notyou'))
def get_link(message):
    f = open(str(message.chat.id) + 'subs.txt', 'a')
    f.close()
    with open(str(message.chat.id) + 'subs.txt', 'r') as f:
        for s in f:
            if s == message.text + "\n":
                return

    with open(str(message.chat.id) + 'subs.txt', 'a') as f:
        f.write(message.text + "\n")

#######################################################################################

def parser(link):
    r = requests.get(link)
    r.encoding='utf-8'
    soup = bs(r.text, 'html.parser')
    s = str(soup.title)
    print(s[7:-20])
    return s[7:-20]

##################################InlineButtonHandler#################################

@bot.callback_query_handler(func=lambda call: True)
def channel_links_parser(query):
    data = query.data
    chat_id = query.from_user.id

    if data.startswith('new_'):
        """ Instruction massage """
        bot.send_message(chat_id, 
                         "Now type a full link to you sub channel \n" +
                         "Also you can write full links whenewer you want, \n" +
                         "This bot will add it in your sublist :)")

    elif data.startswith('channel'):
        """ channels list """
        keyboard = telebot.types.InlineKeyboardMarkup()
        with open(str(chat_id) + 'subs.txt', 'r') as f:
            for i, line in enumerate(f):
                s = parser(line[:-1])
                keyboard.add(telebot.types.InlineKeyboardButton(s, callback_data=str(i) + "chan"))
        bot.send_message(chat_id,
                         "There are your channels (tap to see some videos):",
                         reply_markup=keyboard)

    elif data.find("chan") != -1:
        """ Link to the channel and the name of it """
        keyboard = telebot.types.InlineKeyboardMarkup()

        print(data)

        data = str(data)
        count = data[:data.find("chan")]

        count = int(count)
        keyboard.add(telebot.types.InlineKeyboardButton("To see last 60 uploaded videos press here :)",
                                                        callback_data=str(count) + "vidosis"))
        # keyboard.add(telebot.types.InlineKeyboardButton("To delete this channel press this button",
        #                                                 callback_data=str(count) + "delete"))


        with open(str(chat_id) + 'subs.txt', 'r') as f:
            name = ""
            link = ""
            for i, line in enumerate(f, start=0):
                if i == count:
                    name = parser(line[:-1])
                    link = line[:-1]
            bot.send_message(chat_id,
                             name + "\n" + link,
                             reply_markup=keyboard)

    elif data.find("vid") != -1:
        """ Video names and links parsing """
        count = data[:data.find("vidos")]
        keyboard = telebot.types.InlineKeyboardMarkup()
        count = int(count)
        link = ""
        with open(str(chat_id) + 'subs.txt', 'r') as f:
            for i, line in enumerate(f, start=0):
                if i == count:
                    link = line[:-1]
                    break

        r = requests.get(link)
        r.encoding='utf-8'

        soup   = bs(r.text, 'html.parser')
        name   = soup.select("span")
        name_1 = name[1]
        canell = (name_1.text)

        print("Ok1")

        names = []
        z = 0
        for title in soup.select("div p"):
            k = title.find('a')
            if k is not None:
                tmp = k.text

                if re.search(canell, tmp):
                    a = 1
                else:
                    z += 1
                    if z >= 2:
                        names.append(tmp)

        print("Ok2")
        links = []
        for a in soup.find_all('a', href=True):
            link = (a['href'])

            if re.search(r'com/watch\b', link):
                links.append(link)

        for i in range(len(links)):
            keyboard.add(telebot.types.InlineKeyboardButton(names[i], url=links[i]))

        bot.send_message(
            chat_id,
            "There you can find 60 last videos from selected channel\n:)",
            reply_markup=keyboard
        )

#######################################################################################



bot.polling(none_stop=False)

