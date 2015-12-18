# -*- coding: utf-8 -*-
#!/usr/local/bin/python
import json
import telebot
import requests
from datetime import datetime

API_TOKEN = '146952018:AAEL5s1Q--lhxnZO7lYlFk7WVejYXavQ25k'

bot = telebot.TeleBot(API_TOKEN)

_logger = telebot.logger

# Handle '/start' and '/help'
@bot.message_handler(commands=['ajuda'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, u"""\
Olá, sou o bot não oficial to Tesouro Direto
Escreve /taxas para ver as últimas taxas do TD.
Escreve /tudo para ver os últimos preços do TD.
Para qualqer dúvida, contate o autor: @jaime_GrupoCITEC
""")

@bot.message_handler(commands=['tudo'])
def precos(message):
    chat_id = message.chat.id
    data = get_data()
    if data:
        bot.send_message(chat_id, ''.join(data))
    else:
        bot.send_message(chat_id, u'Ocorreu algum erro na consulta dos dados')

@bot.message_handler(commands=['taxas'])
def taxas(message):
    chat_id = message.chat.id
    data = get_data(u'{nom} | C: {txc}% V: {txv}%\n')
    if data:
        bot.send_message(chat_id, ''.join(data))
    else:
        bot.send_message(chat_id, u'Ocorreu algum erro na consulta dos dados')

def get_data(myFormat=None):
    if myFormat is None:
        myFormat = u'{nom} | C: {txc}% / R${puc} | V: {txv}% / R${puv}\n'
    # Get last update data
    url = 'http://tdireto.com/ws/cotacaoPorDiaWS.php?dt=%(day)02d%%2F%(month)02d%%2F%(year)d&dcn=0' % {
        'day': datetime.today().day,
        'month': datetime.today().month,
        'year': datetime.today().year,
    }
    _logger.info("url = %s" % (url, ))
    jsjson = requests.get(url)
    content = jsjson.content.decode("utf-8")
    content = json.loads(content)
    _logger.info("content = %s" % (content, ))
    if 'data' not in content.keys() or not content['data']:
        date = content.get('dta', False)
        if date:
            url = 'http://tdireto.com/ws/cotacaoPorDiaWS.php?dt=%(day)02d%%2F%(month)02d%%2F%(year)d&dcn=0' % {
                'day': int(date.split(' ')[0].split('/')[0]),
                'month': int(date.split(' ')[0].split('/')[1]),
                'year': int(date.split(' ')[0].split('/')[2]),
            }
            _logger.info("url = %s" % (url, ))
            jsjson = requests.get(url)
            content = jsjson.content.decode("utf-8")
            content = json.loads(content)
            _logger.info("content = %s" % (content, ))
    if 'data' in content.keys():
        data = content['data']
        last_data = {}
        for row in data:
            if row['tid'] not in last_data.keys():
                last_data[row['tid']] = {}
            if not last_data[row['tid']] or last_data[row['tid']]['dh'] < row['dh']:
                last_data[row['tid']] = row

        response = []
        for tid, row in last_data.items():
            response += [myFormat.format(**row)]
        response = list(sorted(response))
        _logger.info("response = %s" % (response, ))
        return response
    else:
        return None

bot.polling()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
